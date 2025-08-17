import redis, time, uuid, requests, boto3, os, json
from io import BytesIO

from dotenv import load_dotenv
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
r = redis.Redis(host="redis", port=6379, db=0, decode_responses=True)

# Db url 가져오기
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
BASE_URL = os.getenv("BASE_URL")
SERVICE_TOKEN = os.getenv("SERVICE_TOKEN")
NOTIFY_ENDPOINT = os.getenv("NOTIFY_ENDPOINT")

AWS_REGION = os.getenv("AWS_S3_REGION")
AWS_BUCKET = os.getenv("AWS_S3_BUCKET_NAME")
AWS_ACCESS_KEY = os.getenv("AWS_S3_ACCESS_KEY")
AWS_SECRET_KEY = os.getenv("AWS_S3_SECRET_KEY")
PRESIGNED_EXPIRATION = int(os.getenv("AWS_S3_PRESIGNED_URL_EXPIRATION", "300")) 

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

    # 3개 payload 생성 및 점검 출력 함수 호출
    original_result, translation_payload, emotion_payload = create_payloads_and_check(result)

    # image_generation은 원본 전체 result 전달
    step_id_img = str(uuid.uuid4())
    r.hset(f"task:{step_id_img}", mapping={
        "status": "queued",
        "payload": original_result,
        "pipelineId": pipeline_id,
        "order": base_order + 1
    })
    r.lpush("task_queue", step_id_img)
    print(f"[STEP {base_order}] 다음 step 생성 및 큐 등록 완료: {step_id_img}")

    # story_translation: translation_payload JSON 직렬화하여 전달
    step_id_trans = str(uuid.uuid4())
    r.hset(f"task:{step_id_trans}", mapping={
        "status": "queued",
        "payload": json.dumps(translation_payload, ensure_ascii=False),
        "pipelineId": pipeline_id,
        "order": int(f"{base_order}1")
    })
    r.lpush("task_queue", step_id_trans)
    print(f"[STEP {int(f'{base_order}')}] 다음 step 생성 및 큐 등록 완료: {step_id_trans}")

    # emotion_classification: emotion_payload JSON 직렬화하여 전달
    step_id_emo = str(uuid.uuid4())
    r.hset(f"task:{step_id_emo}", mapping={
        "status": "queued",
        "payload": json.dumps(emotion_payload, ensure_ascii=False),
        "pipelineId": pipeline_id,
        "order": int(f"{base_order}2")
    })
    r.lpush("task_queue", step_id_emo)
    print(f"[STEP {int(f'{base_order}')}] 다음 step 생성 및 큐 등록 완료: {step_id_emo}")

# scene parser 큐 생성 유틸
def create_payloads_and_check(result: str):
    """
    scene parser 결과 JSON 문자열에서
    3개 payload 생성 후 각각 내용 출력 (점검용)

    Args:
        result (str): scene parser 결과 JSON 문자열

    Returns:
        tuple:
            original_result (str): 이미지 생성용 원본 결과
            translation_payload (list): 번역용 payload (scene_number, story)
            emotion_payload (list): 감정분석용 payload (scene_number, mood)
    """
    parsed_result = json.loads(result)
    scenes = parsed_result.get("scenes", [])

    # 이미지 생성용은 원본 그대로
    original_result = result
    # 번역용 payload: scene_number, summary -> story
    translation_payload = [
        {"scene_number": scene["scene_number"], "story": scene["story"]}
        for scene in scenes
    ]

    # 감정분석용 payload: scene_number, mood
    emotion_payload = [
        {"scene_number": scene["scene_number"], "mood": scene["mood"]}
        for scene in scenes
    ]
    return original_result, translation_payload, emotion_payload

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

    images = manager.process(input_text)  # List[bytes]

    with crud.get_session() as db:
        for i, image_bytes in enumerate(images, 1):
            # S3 업로드
            s3_key = f"{pipeline_id}/scene_{i}.png"
            image_url = upload_image_to_s3(image_bytes, s3_key)

            # DB에 URL 저장
            crud.save_scene_image_url(
                db=db,
                pipeline_id=pipeline_id,
                scene_number=i,
                image_url=image_url
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
            try:
                scene_number = item["scene_number"]
                mood = item["mood"]
                result = emotion_classifer_manager.process(mood)
                emotion = result.get('emotion')
                if emotion is None:
                    emotion = "unknown"

                crud.save_mood(db, pipeline_id, scene_number, emotion)
                emotions.append({
                    "scene_number": scene_number,
                    "emotion": emotion
                })
            except Exception as e:
                print(f"[ERROR] scene_number {item.get('scene_number')}: {e}")
                crud.save_mood(db, pipeline_id, scene_number, "error")
    return "success"

# 완료 알림용 로직
def notify_fairytale_completion(input_text: str, pipeline_id: str, crud: PipelineCRUD) -> str:
    """
    동화 생성 완료를 웹서버에 알리는 함수

    Args:
        input_text (str): 생성에 사용된 원본 입력 (사용하지 않지만 구조적 일관성 유지용)
        pipeline_id (str): 조회 및 알림용 파이프라인 ID
        crud (PipelineCRUD): DB 접근용 CRUD 인스턴스

    Returns:
        str: 성공 여부
    """
    db = crud.get_session()
    try:
        payload = crud.get_result_payload(db, pipeline_id)
        url = f"{BASE_URL}{NOTIFY_ENDPOINT}"
        headers = {
            "Authorization": f"Bearer {SERVICE_TOKEN}",
            "Content-Type": "application/json"
        }

        response = requests.post(url, json=payload, headers=headers, timeout=5)
        response.raise_for_status()
        print(f"Notification sent successfully for pipeline {pipeline_id}.")
        return "success"
    except Exception as e:
        print(f"Failed to notify fairytale completion: {e}")
        return "failed"
    finally:
        db.close()
    
# 분기용 유틸 함수 3개
def use_db_for_logic(logic_fn):
    # DB를 필요로 하는 함수명을 리스트로 관리
    db_required_fns = {"image_maker", "en_ko_translator", "emotion_classifier", "notify_fairytale_completion"}
    return logic_fn.__name__ in db_required_fns

def is_scene_parser_logic(logic_fn):
    db_required_fns = {"scene_parser"}
    return logic_fn.__name__ in db_required_fns

def is_terminal(logic_fn):
    db_required_fns = {"emotion_classifier", "en_ko_translator", "notify_fairytale_completion"}
    return logic_fn.__name__ in db_required_fns

# s3 업로드용 유틸 함수
def upload_image_to_s3(image_bytes: bytes, s3_key: str) -> str:
    """
    S3에 이미지 업로드 후 public URL 반환
    """
    file_obj = BytesIO(image_bytes)

    # S3에 업로드
    s3_client.upload_fileobj(
        Fileobj=file_obj,
        Bucket=AWS_BUCKET,
        Key=s3_key,
        ExtraArgs={"ContentType": "image/png", "ACL": "public-read"}  # 퍼블릭 읽기 권한
    )

    # 그냥 URL 생성 (리전 필요)
    url = f"https://{AWS_BUCKET}.s3.{AWS_REGION}.amazonaws.com/{s3_key}"
    return url

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

# boto3 S3 클라이언트 생성
s3_client = boto3.client(
    "s3",
    region_name=AWS_REGION,
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY,
)

# Step 매핑
step_map = {
    1: ko_en_translator,
    2: story_writer,
    3: scene_parser,
    4: prompt_maker,
    5: image_maker,
    31: en_ko_translator,
    32: emotion_classifier,
    6: notify_fairytale_completion
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
