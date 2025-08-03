import redis
import time
import uuid
from functools import partial

from dotenv import load_dotenv
import os
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

# translator 로직
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

# db 분기용 유틸함수
def use_db_for_logic(logic_fn):
    # DB를 필요로 하는 함수명을 리스트로 관리
    db_required_fns = {"image_maker"}
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
