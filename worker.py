import redis
import time
import uuid

from dotenv import load_dotenv
import os, json
from db.pipeline_crud import PipelineCRUD

from translator.translator_selector import TranslatorSelector
from translator.translator_manager import TranslatorManager
from story_writer.story_writer_selector import StoryWriterSelector
from story_writer.story_writer_manager import StoryWriterManager
from scene_parser.scene_parser_selector import SceneParserSelector
from scene_parser.scene_parser_manager import SceneParserManager
from prompt_maker.prompt_maker_selector import PromptMakerSelector
from prompt_maker.prompt_maker_manager import PromptMakerManager
from emotion_classifier.emotion_classifier_selector import EmotionClassifierSelector
from emotion_classifier.emotion_classifier_manager import EmotionClassifierManager
from image_maker.image_maker_selector import ImageMakerSelector
from image_maker.image_maker_manager import ImageMakerManager

# Redis 연결
r = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)

# Db url 가져오기
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

# 큐 관련 처리
def enqueue_next_step(current_task_data, result):
    """
    현재 task 정보를 바탕으로 다음 step을 생성하고 큐에 등록

    Args:
        current_task_data (dict): 현재 step의 task 데이터 (stepId 포함 X)
        result (str): 현재 step 처리 결과
    """
    next_order = int(current_task_data['order']) + 1
    next_step_id = str(uuid.uuid4())

    r.hset(f"task:{next_step_id}", mapping={
        "status": "queued",
        "payload": result,
        "pipelineId": current_task_data['pipelineId'],
        "order": next_order
    })

    r.lpush("task_queue", next_step_id)
    print(f"[STEP {current_task_data['order']}] 다음 step 생성 및 큐 등록 완료: {next_step_id}")

def enqueue_next_steps_after_scene_parser(current_task_data, result):
    """
    scene parser 이후 분기 처리: 3개의 다음 step을 각각 등록

    Args:
        current_task_data (dict): 현재 step의 task 데이터 (stepId 포함 X)
        result (str): scene parser의 결과 (JSON 문자열)
    """
    base_order = int(current_task_data['order'])
    pipeline_id = current_task_data['pipelineId']

    parsed_result = json.loads(result)
    scenes = parsed_result.get("scenes", [])

    # image_generation은 원본 전체 result 전달
    step_id_img = str(uuid.uuid4())
    r.hset(f"task:{step_id_img}", mapping={
        "status": "queued",
        "payload": result,
        "pipelineId": pipeline_id,
        "order": base_order + 1
    })
    r.lpush("task_queue", step_id_img)

    # story_translation: scene_number, summary만 추출
    translation_payload = [
        {"scene_number": scene["scene_number"], "story": scene["summary"]}
        for scene in scenes
    ]
    step_id_trans = str(uuid.uuid4())
    r.hset(f"task:{step_id_trans}", mapping={
        "status": "queued",
        "payload": json.dumps(translation_payload),
        "pipelineId": pipeline_id,
        "order": int(f"{base_order}1")
    })
    r.lpush("task_queue", step_id_trans)

    # emotion_classification: scene_number, mood만 추출
    emotion_payload = [
        {"scene_number": scene["scene_number"], "mood": scene["mood"]}
        for scene in scenes
    ]
    step_id_emo = str(uuid.uuid4())
    r.hset(f"task:{step_id_emo}", mapping={
        "status": "queued",
        "payload": json.dumps(emotion_payload),
        "pipelineId": pipeline_id,
        "order": int(f"{base_order}2")
    })
    r.lpush("task_queue", step_id_emo)

# ko_en_translator 로직
def ko_en_translator(input_text:str):
    translator = TranslatorSelector.get_translator("marian")
    translator_manager = TranslatorManager(translator)
    return translator_manager.process(input_text)

# story_writer 로직
def story_writer(input_text:str):
    story_writer = StoryWriterSelector.get_writer("llama")
    story_manager = StoryWriterManager(story_writer)
    return story_manager.process(input_text)

# scene_parser 로직
def scene_parser(input_text:str):
    parser = SceneParserSelector.get_parser(parser_type="llama")
    manager = SceneParserManager(parser)
    return manager.process(input_text)

# prompt_maker 로직
def prompt_maker(input_text:str):
    prompt_maker = PromptMakerSelector.get_prompt_maker("llama")
    manager = PromptMakerManager(prompt_maker)
    return manager.process(input_text)

# image_maker 로직
def image_maker(input_text: str, pipeline_id: str, crud: PipelineCRUD):
    image_maker = ImageMakerSelector.get_image_maker('dream_shaper')
    manager = ImageMakerManager(image_maker)

    images = manager.process(input_text)

    with crud.get_session() as db:
        for i, image_bytes in enumerate(images, 1):
            crud.save_scene_image(
                db=db,
                pipeline_id=pipeline_id,
                scene_number=i,
                image_bytes=image_bytes
            )

    return "success"

# en_ko_translator 로직
def en_ko_translator(input_text: str, pipeline_id: str, crud: PipelineCRUD):
    """
    영어 story를 한국어로 번역하고 DB에 저장
    input_text: '[{"scene_number": 1, "story": "...."}, ...]' 형태의 JSON 문자열
    """
    translator = TranslatorSelector.get_translator("nllb")
    translator_manager = TranslatorManager(translator)

    data = json.loads(input_text)
    translated = []

    with crud.get_session() as db:
        for item in data:
            scene_number = item["scene_number"]
            story_en = item["story"]
            story_ko = translator_manager.process(story_en)

            # DB에 저장
            crud.save_scene_story(db, pipeline_id, scene_number, story_ko)

            translated.append({
                "scene_number": scene_number,
                "story_ko": story_ko
            })

    return json.dumps(translated, ensure_ascii=False)

# emotion_classifer 로직
def emotion_classifier(input_text: str, pipeline_id: str, crud: PipelineCRUD):
    classifer = EmotionClassifierSelector.get_emotion_classifier("minilm")
    emotion_classifer_manager = EmotionClassifierManager(classifer)

    data = json.loads(input_text)
    emotions = []

    with crud.get_session() as db:
        for item in data:
            scene_number = item["scene_number"]
            mood = item["mood"]
            emotion = emotion_classifer_manager.process(mood)

            # DB에 저장
            crud.save_mood(db, pipeline_id, scene_number, mood)

            emotions.append({
                "scene_number": scene_number,
                "emotion": emotion
            })

# next enque 분기용 유틸 함수 3개
def use_db_for_logic(logic_fn):
    # DB를 필요로 하는 함수명을 리스트로 관리
    db_required_fns = {"image_maker", "en_ko_translator", "emotion_classifer"}
    return logic_fn.__name__ in db_required_fns

def is_scene_parser_logic(logic_fn):
    db_required_fns = {"scene_parser"}
    return logic_fn.__name__ in db_required_fns

def is_terminal(logic_fn):
    db_required_fns = {"image_maker", "emotion_classifer", "en_ko_translator"}
    return logic_fn.__name__ in db_required_fns

# step 함수
def step(task_data, logic):
    payload = task_data['payload']

    if use_db_for_logic(logic):
        result = logic(input_text=payload, pipeline_id=task_data['pipelineId'], crud=crud)
    else:
        result = logic(input_text=payload)

    r.hset(f"task:{task_data['stepId']}", mapping={
        "status": "done",
        "result": result
    })

    if is_terminal(logic):
        return
    elif is_scene_parser_logic(logic):
        enqueue_next_steps_after_scene_parser(task_data, result)
    else:
        enqueue_next_step(task_data, result)

# db crud 객체 생성
crud = PipelineCRUD(DATABASE_URL)

# Step 매핑
step_map = {
    1: ko_en_translator,
    2: story_writer,
    3: scene_parser,
    4: prompt_maker,
    5: image_maker,
    31: en_ko_translator,
    32: emotion_classifier
}

# 워커 루프
print("워커 시작됨. 작업 대기 중...")

while True:
    try:
        # 1. 대기열에서 작업 꺼내기
        _, step_id = r.brpop("task_queue")
        task_key = f"task:{step_id}"

        # 2. 해시에서 작업 데이터 읽기
        task_data = r.hgetall(task_key)

        # 3. 필수 필드 확인
        required_fields = ["status", "payload", "pipelineId", "order"]
        if not all(field in task_data for field in required_fields):
            print(f"[경고] 필수 필드 누락: {task_data}")
            r.hset(task_key, "status", "failed")
            continue

        # 4. 처리 시작 전 상태 업데이트
        r.hset(task_key, "status", "processing")
        task_data["stepId"] = step_id  # step 함수에 전달

        # 5. 스텝 함수 실행
        order = int(task_data["order"])
        step_fn = step_map.get(order)

        if step_fn:
            step(task_data, step_fn)
        else:
            print(f"[경고] 정의되지 않은 step order: {order}")
            r.hset(task_key, "status", "failed")

    except Exception as e:
        print(f"[에러] 처리 중 예외 발생: {e}")
        time.sleep(1)
