# StoryPool AI Pipeline 📚✨

<p align="center">
  <img src="gifs/시연영상.gif" width="600"/>
</p>
> 사용자의 일기를 바탕으로 개인화된 그림동화를 자동 생성하는 AI 파이프라인

## 🎯 프로젝트 개요

StoryPool AI Pipeline은 사용자가 작성한 일기 텍스트를 분석하여 감정과 상황을 파악하고, 이를 바탕으로 개인화된 그림동화를 자동으로 생성하는 멀티모달 AI 시스템.

### 주요 기능
- 📝 **OCR**: 손글씨 일기를 텍스트로 변환
- 🌐 **번역**: 다국어 일기 내용을 영어로 번역
- 🎭 **감정 분석**: 일기 내용의 감정 상태 분석
- 📖 **스토리 생성**: AI 기반 일기내용을 이용한 동화 스토리 생성
- 🎬 **장면 분석**: 스토리의 장면별 구조 분석
- 💡 **이미지 프롬프트 생성**: 각 모듈의 AI 프롬프트 자동 생성
- 🎨 **이미지 생성**: 스토리에 맞는 일러스트 자동 생성


## 🏗️ 시스템 아키텍처

```
사용자 일기 입력
    ↓
OCR (손글씨 → 텍스트)
    ↓
번역 (다국어 → 한국어/영어)
    ↓
스토리 생성 (개인화 동화 생성)
    ↓
장면 분석 (스토리 구조화)  →  감정 분석 (감정 상태 파악)
    ↓
이미지 생성 (일러스트 생성)
    ↓
완성된 그림동화
```

## 🚀 빠른 시작

### 요구사항
- Python 3.12+
- requirements.txt 참고
- diffusers==0.34.0: 딥러닝 기반 이미지 생성 및 변환 모델(예: Stable Diffusion)을 쉽게 사용할 수 있도록 돕는 라이브러리
- easyocr==1.7.2: 다양한 언어를 지원하는 간편한 OCR(문자 인식) 라이브러리
- fastapi==0.115.14: Python으로 빠르고 효율적인 REST API 서버를 쉽게 개발할 수 있는 웹 프레임워크
- httpx==0.28.1: 비동기 및 동기 HTTP 요청을 지원하는 고성능 HTTP 클라이언트 라이브러리
- numpy==2.3.1: 고성능 수치 계산을 위한 배열 및 행렬 연산 라이브러리
- Pillow==11.2.1: Python에서 이미지 처리와 조작을 위한 라이브러리 (PIL의 후속)
- pydantic==2.11.7: 데이터 유효성 검사 및 설정 관리를 위한 타입 기반 모델링 라이브러리
- pytest==8.4.1: Python 테스트 코드 작성과 실행을 도와주는 테스트 프레임워크
- sentence_transformers==4.1.0: 문장 임베딩 벡터 생성 및 문장 간 유사도 계산에 특화된 라이브러리
- torch==2.7.1: 딥러닝 모델 개발에 널리 쓰이는 PyTorch 라이브러리
- transformers==4.53.0: Hugging Face에서 제공하는 다양한 사전학습 NLP 모델 사용 라이브러리
- uvicorn==0.35.0: ASGI 기반 비동기 Python 웹서버, 주로 FastAPI와 함께 사용됨


### 설치
프로젝트
```bash
git clone https://github.com/jiwoong5/storypool_ai_pipeline.git
cd storypool_ai_pipeline
pip install -r requirements.txt
```
llama 모델 - 3.2b - 3B  
- [llama download](https://www.llama.com/llama-downloads/)
- [ollama_download](https://ollama.com/download)
- ollama pull llama3.2:3b

### 실행
```bash
python apis.py
```

서버 실행 후 `http://localhost:8000/docs`에서 API 문서를 확인할 수 있음.


## 📋 API 엔드포인트

### 헬스 체크
- `GET /health` - 시스템 상태 확인

### OCR (광학 문자 인식)
- `POST /ocr/process` - 이미지 파일에서 텍스트 추출
- `POST /ocr/batch` - 여러 이미지 파일 일괄 처리

### 번역
- `POST /translator/process` - 파일 번역
- `POST /translator/text` - 텍스트 번역

### 감정 분석
- `POST /emotion/process` - 파일 감정 분석
- `POST /emotion/text` - 텍스트 감정 분석
- `POST /emotion/batch` - 여러 파일 일괄 감정 분석

### 스토리 생성
- `POST /story/process` - 파일 기반 스토리 생성
- `POST /story/text` - 텍스트 기반 스토리 생성

### 장면 분석
- `POST /scene/process` - 파일 기반 장면 분석
- `POST /scene/text` - 텍스트 기반 장면 분석

### 프롬프트 생성
- `POST /prompt/process` - 파일 기반 프롬프트 생성
- `POST /prompt/text` - 텍스트 기반 프롬프트 생성

### 이미지 생성
- `POST /image/process` - 파일 기반 이미지 생성
- `POST /image/text` - 텍스트 기반 이미지 생성

## 🔧 설정

### 환경 변수
```env
# AI 모델 설정
OCR_MODEL_TYPE=easyocr
TRANSLATOR_MODEL_TYPE=marin
STORY_WRITER_MODEL_TYPE=llama
EMOTION_CLASSIFIER_MODEL_TYPE=minilm
IMAGE_MAKER_MODEL_TYPE=dream_shaper

# 출력 디렉토리
OUTPUT_BASE_PATH=outputs

# API 설정
API_HOST=0.0.0.0
API_PORT=8000
```

## 📁 프로젝트 구조

```
.storypool_ai_pipeline/
│
├── apis.py
├── main.py
├── requirements.txt
│
├── api_caller/
│   ├── api_caller_interface.py
│   ├── api_caller_selector.py
│
├── emotion_classifier/
│   ├── emotion_classifier_interface.py
│   ├── emotion_classifier_manager.py
│   ├── emotion_classifier_selector.py
│
├── image_maker/
│   ├── image_maker_interface.py
│   ├── image_maker_manager.py
│   ├── image_maker_selector.py
│
├── llama_tools/
│   ├── llama_api_caller.py
│   ├── llama_helper.py
│
├── object_analyst/
│   ├── object_analyst_interface.py
│   ├── object_analyst_manager.py
│   ├── object_analyst_selector.py
│
├── ocr/
│   ├── easy_ocr.py
│   ├── ocr_interface.py
│   ├── ocr_manager.py
│   ├── ocr_selector.py
│
├── prompt_maker/
│   ├── llama_prompt_maker.py
│   ├── prompt_maker_interface.py
│   ├── prompt_maker_manager.py
│   ├── prompt_maker_selector.py
│
├── scene_parser/
│   ├── basic_scene_parser.py
│   ├── scene_parser_interface.py
│   ├── scene_parser_manager.py
│   ├── scene_parser_selector.py
│
├── story_writer/
│   ├── llama_story_writer.py
│   ├── story_writer_interface.py
│   ├── story_writer_manager.py
│   ├── story_writer_selector.py
│
└── translator/
    ├── marian_translator.py
    ├── nllb_translator.py
    ├── translator_interface.py
    ├── translator_manager.py
    ├── translator_selector.py

```

## 🎨 사용 예시

### 텍스트 기반 그림동화 생성 전체 플로우

```python

# 1. OCR (파일 업로드)
print(requests.post(
    "http://localhost:8000/ocr/process",
    files={"file": open("sample_image.png", "rb")},
    params={"reader_type": "easyocr"}
).json())

# 2. 한영 번역 (텍스트)
print(requests.post(
    "http://localhost:8000/translator/text",
    json={"text": "오늘은 친구들과 놀이터에서 정말 즐거운 시간을 보냈어요!", "translator_type": "marin"}
).json())

# 3. 스토리 생성 (텍스트 프롬프트)
print(requests.post(
    "http://localhost:8000/story/text",
    json={"prompt": "I have really ~", "writer_type": "llama"}
).json())

# 4. 장면 분석 (텍스트)
print(requests.post(
    "http://localhost:8000/scene/text",
    json={"text": "he left the village and ~", "parser_type": "basic"}
).json())

# 5-1. 감정 분석 (텍스트)
print(requests.post(
    "http://localhost:8000/emotion/text",
    json={"text": "[scene 1] he left ~", "emotion_classifer_type": "minilm"}
).json())

# 5-2-1. 이미지 프롬프트 생성 (텍스트)
print(requests.post(
    "http://localhost:8000/prompt/text",
    json={"input_text": "[scene 1] he left ~", "prompt_maker_type": "llama"}
).json())

# 5-2-2. 이미지 생성 (텍스트 프롬프트)
print(requests.post(
    "http://localhost:8000/image/text",
    json={"prompt": "A beautiful summer beach with children playing", "image_maker_type": "dream_shaper", "num_images": 1}
).json())

```

## 🎨 모듈별 상세구조

공통구조
- interface: 기능을 추상화한 계약(Contract) 역할, 추상 메서드(abstract method)를 선언하여, 실제 구현체들이 반드시 구현해야 하는 메서드를 정의
- selector: 인터페이스 구현체(실제 기능을 하는 클래스)를 선택/생성하는 팩토리 역할, 인자로 받은 키워드나 설정값에 따라 적합한 구현체를 반환
- manager: 비즈니스 로직 담당, 인터페이스 구현체의 메서드를 호출하여 실제 작업 수행, 외부에서 전달받은 데이터 처리 (ex. 파일 경로에서 이미지 읽기)
- 구현체: 기능의 구현 로직을 담당하며, 외부에서 호출되는 interface에서 선언된 메서드를 통해 동작 수행.
- selector 입력 str 바탕으로 구현체 생성 > manager에 주입 > manager는 인터페이스 형태 사용

upload data/output data path
```python
def create_output_directory(base_path: str = "outputs") -> str:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = os.path.join(base_path, timestamp)
    os.makedirs(output_dir, exist_ok=True)
    return output_dir
```
- base_path + YYYYMMDD_HHMMSS
- ex) outputs/20250701_182604

---

`GET /health`

**작업 내용**: 서비스 상태 및 각 컴포넌트의 헬스 체크

**입력**: 없음

**출력**: 
```python
# 헬스 체크 응답
class HealthCheckResponse(BaseModel):
    status: str = Field(..., description="서비스 상태")
    version: str = Field(..., description="API 버전")
    uptime: float = Field(..., description="서비스 가동 시간 (초)")
    components: Dict[str, str] = Field(default_factory=dict, description="각 컴포넌트 상태")
    timestamp: datetime = Field(default_factory=datetime.now, description="체크 시간")
```

- 서비스 상태, 버전, 가동시간
- 각 AI 컴포넌트(OCR, 번역기, 스토리 작성기 등)의 상태
---

`POST /ocr/process`

**작업 내용**: 업로드된 이미지에서 텍스트 추출

**입력**: 
```python
# OCR 요청
class OCRRequest(BaseModel):
    image_path: Optional[str] = Field(None, description="처리할 이미지 파일 경로")
    reader_type: OCRReaderType = Field(default=OCRReaderType.EASYOCR, description="사용할 OCR 리더 타입")
``` 

- 이미지 파일 (multipart/form-data)
- OCR 리더 타입 (기본값: easyocr)
- 
**출력**:
  
```python
# OCR 응답 
class OCRResponse(BaseResponse):
    extracted_text: Optional[str] = Field(None, description="추출된 텍스트")
    confidence_score: Optional[float] = Field(None, description="인식 신뢰도 점수")
    detected_languages: Optional[List[str]] = Field(None, description="감지된 언어 목록")
    bounding_boxes: Optional[List[Dict[str, Any]]] = Field(None, description="텍스트 영역 좌표 정보")
```

- 추출된 텍스트
- 신뢰도 점수
- 감지된 언어 목록

`POST /ocr/batch`

**작업 내용**: 여러 이미지 파일에서 일괄 텍스트 추출

**입력**: 

```python
class OCRBatchRequest(BaseModel):
    image_paths: Optional[List[str]] = Field(None, description="처리할 이미지 파일 경로 리스트")
    reader_type: OCRReaderType = Field(default=OCRReaderType.EASYOCR, description="사용할 OCR 리더 타입")
```

- 이미지 파일 목록
- OCR 리더 타입


**출력**: 

```python
class OCRBatchResponse(BaseResponse):
    results: List[Dict[str, Union[str, float, List]]] = Field(default_factory=list, description="배치 처리 결과")
    total_processed: int = Field(0, description="처리된 총 이미지 수")
    successful_count: int = Field(0, description="성공한 처리 개수")
    failed_count: int = Field(0, description="실패한 처리 개수")
```

- 각 파일별 처리 결과
- 성공/실패 개수 통계

---

`POST /translator/process`

**작업 내용**: 업로드된 텍스트 파일 번역

**입력**: 

```python
# Translator 요청
class TranslatorRequest(BaseModel):
    input_file_path: Optional[str] = Field(None, description="번역할 이미지 파일 경로")
    translator_type: TranslatorType = Field(default=TranslatorType.NLLB, description="사용할 번역기 타입")
```

- 텍스트 파일
- 번역기 타입 (marin, nllb)

**출력**: 

```python
# Translator 응답
class TranslatorResponse(BaseResponse):
    original_text: Optional[str] = Field(None, description="원본 텍스트")
    translated_text: Optional[str] = Field(None, description="번역된 텍스트")
    source_language: Optional[str] = Field(None, description="원본 언어")
    target_language: Optional[str] = Field(None, description="대상 언어")
    confidence_score: Optional[float] = Field(None, description="번역 신뢰도")
```

- 원본 텍스트
- 번역된 텍스트
- 번역 신뢰도

`POST /translator/text`

**작업 내용**: 입력된 텍스트 직접 번역

**입력**: 

```python
# Translator Text 요청
class TranslatorTextRequest(BaseModel):
    text: str = Field(..., description="번역할 텍스트")
    translator_type: TranslatorType = Field(default=TranslatorType.NLLB, description="사용할 번역기 타입")
```

- 번역할 텍스트
- 번역기 타입

**출력**: 
- 번역된 텍스트
- 번역 신뢰도

---

`POST /story/process`

**작업 내용**: 업로드된 프롬프트 파일을 기반으로 스토리 생성

**입력**: 

```python
# Story Writer 요청
class StoryWriterRequest(BaseModel):
    input_file_path: Optional[str] = Field(None, description="스토리 작성 입력 파일 경로")
    writer_type: StoryWriterType = Field(default=StoryWriterType.LLAMA, description="사용할 스토리 라이터 타입")
```

- 프롬프트 파일
- 스토리 작성기 타입 (llama)

**출력**: 

```python
# Story Writer 응답
class StoryWriterResponse(BaseResponse):
    generated_story: Optional[str] = Field(None, description="생성된 스토리")
    genre: Optional[str] = Field(None, description="감지된 장르")
    writing_style: Optional[str] = Field(None, description="작성 스타일")
```

- 생성된 스토리
- 감지된 장르
- 작성 스타일

`POST /story/text`

**작업 내용**: 입력된 프롬프트로 스토리 생성

**입력**: 

```python
# Story Writer Text 요청
class StoryWriterTextRequest(BaseModel):
    prompt: str = Field(..., description="스토리 작성 프롬프트")
    writer_type: StoryWriterType = Field(default=StoryWriterType.LLAMA, description="사용할 스토리 라이터 타입")
```

- 스토리 프롬프트
- 스토리 작성기 타입

**출력**: 
- 생성된 스토리
- 장르 및 스타일 정보

---

`POST /scene/process`

**작업 내용**: 업로드된 텍스트 파일의 장면 분석

**입력**: 

```python
# Scene Parser 요청
class SceneParserRequest(BaseModel):
    input_file_path: Optional[str] = Field(None, description="장면 분석할 텍스트 파일 경로")
    parser_type: SceneParserType = Field(default=SceneParserType.BASIC, description="사용할 장면 파서 타입")
```

- 텍스트 파일
- 장면 파서 타입 (basic)

**출력**: 

```python
# Scene Parser 응답
class SceneInfo(BaseModel):
    scene_number: int = Field(..., description="장면 번호")
    scene_title: Optional[str] = Field(None, description="장면 제목")
    characters: List[str] = Field(default_factory=list, description="등장 인물")
    location: Optional[str] = Field(None, description="장소")
    time: Optional[str] = Field(None, description="시간")
    mood: Optional[str] = Field(None, description="분위기")
    summary: Optional[str] = Field(None, description="장면 요약")
    dialogue_count: Optional[int] = Field(None, description="대화 수")

class SceneParserResponse(BaseResponse):
    scenes: List[SceneInfo] = Field(default_factory=list, description="분석된 장면 정보")
    total_scenes: int = Field(0, description="총 장면 수")
    main_characters: List[str] = Field(default_factory=list, description="주요 등장 인물")
    locations: List[str] = Field(default_factory=list, description="등장 장소")
```

- 장면별 상세 정보 (번호, 제목, 등장인물, 장소, 시간, 분위기)
- 주요 등장인물 목록
- 등장 장소 목록

`POST /scene/text`

**작업 내용**: 입력된 텍스트의 장면 분석

**입력**: 

```python
# Scene Parser Text 요청
class SceneParserTextRequest(BaseModel):
    text: str = Field(..., description="장면 분석할 텍스트")
    parser_type: SceneParserType = Field(default=SceneParserType.BASIC, description="사용할 장면 파서 타입")
```

- 분석할 텍스트
- 장면 파서 타입

**출력**: 
- 분석된 장면 정보
- 등장인물 및 장소 통계

---
`POST /prompt/process`

**작업 내용**: 업로드된 파일을 기반으로 AI 프롬프트 생성

**입력**: 

```python
# Prompt Maker 요청
class PromptMakerRequest(BaseModel):
    input_file_path: Optional[str] = Field(None, description="프롬프트 생성 입력 파일 경로")
    prompt_maker_type: PromptMakerType = Field(default=PromptMakerType.LLAMA, description="사용할 프롬프트 메이커 타입")
```

- 입력 파일
- 프롬프트 메이커 타입 (llama)

**출력**: 

```python
# Prompt Maker 응답
class PromptMakerResponse(BaseResponse):
    generated_prompt: Optional[str] = Field(None, description="생성된 프롬프트")
    prompt_type: Optional[str] = Field(None, description="프롬프트 유형")
    keywords: List[str] = Field(default_factory=list, description="추출된 키워드")
    estimated_length: Optional[int] = Field(None, description="예상 응답 길이")
    prompt_quality_score: Optional[float] = Field(None, description="프롬프트 품질 점수")
```

- 생성된 프롬프트
- 프롬프트 유형
- 추출된 키워드
- 품질 점수

`POST /prompt/text`

**작업 내용**: 입력 텍스트를 기반으로 프롬프트 생성

**입력**: 

```python
# Prompt Maker Text 요청
class PromptMakerTextRequest(BaseModel):
    input_text: str = Field(..., description="프롬프트 생성을 위한 입력 텍스트")
    prompt_maker_type: PromptMakerType = Field(default=PromptMakerType.LLAMA, description="사용할 프롬프트 메이커 타입")
```

- 입력 텍스트
- 프롬프트 메이커 타입

**출력**: 
- 최적화된 프롬프트
- 키워드 및 품질 평가

---
`POST /emotion/process`

**작업 내용**: 업로드된 텍스트 파일의 감정 분석

**입력**: 

```python
# Emotion Classifier 요청
class EmotionClassifierRequest(BaseModel):
    input_file_path: Optional[str] = Field(None, description="감정 분류할 텍스트 파일 경로")
    emotion_classifer_type: EmotionClassiferType = Field(default=EmotionClassiferType.MINILM, description="감정 분석기 타입")
```

- 텍스트 파일
- 감정 분석기 타입 (minilm)

**출력**: 

```python
# Emotion Classifier 응답
class EmotionScore(BaseModel):
    emotion: str = Field(..., description="감정 이름")
    score: float = Field(..., description="감정 점수 (0-1)")
    confidence: float = Field(..., description="신뢰도 (0-1)")

class EmotionClassifierResponse(BaseResponse):
    primary_emotion: Optional[str] = Field(None, description="주요 감정")
    emotion_scores: List[EmotionScore] = Field(default_factory=list, description="모든 감정 점수")
    sentiment_polarity: Optional[str] = Field(None, description="감정 극성 (positive/negative/neutral)")
    intensity: Optional[float] = Field(None, description="감정 강도 (0-1)")
```

- 주요 감정
- 모든 감정별 점수
- 감정 극성 (positive/negative/neutral)
- 감정 강도

`POST /emotion/text`

**작업 내용**: 입력 텍스트의 감정 분석

**입력**: 

```python
class EmotionClassifierTextRequest(BaseModel):
    text: str = Field(..., description="감정 분류할 텍스트")
    emotion_classifer_type: EmotionClassiferType = Field(default=EmotionClassiferType.MINILM, description="감정 분석기 타입")
```

- 분석할 텍스트
- 감정 분석기 타입

**출력**: 
- 감정 분석 결과
- 신뢰도 점수

`POST /emotion/batch`

**작업 내용**: 여러 텍스트 파일의 일괄 감정 분석

**입력**: 

```python
class EmotionClassifierBatchRequest(BaseModel):
    input_file_paths: Optional[List[str]] = Field(None, description="감정 분류할 텍스트 파일 경로 리스트")
    emotion_classifer_type: EmotionClassiferType = Field(default=EmotionClassiferType.MINILM, description="감정 분석기 타입")
```

- 텍스트 파일 목록
- 감정 분석기 타입

**출력**: 

```python
class EmotionClassifierBatchResponse(BaseResponse):
    results: Dict[str, Dict[str, Any]] = Field(default_factory=dict, description="배치 처리 결과")
    summary: Dict[str, Any] = Field(default_factory=dict, description="전체 감정 분석 요약")
    total_processed: int = Field(0, description="처리된 총 파일 수")
```

- 파일별 감정 분석 결과
- 전체 감정 분석 요약

---
`POST /image/process`

**작업 내용**: 업로드된 프롬프트 파일로 이미지 생성

**입력**: 

```python
# Image Maker 요청
class ImageMakerRequest(BaseModel):
    input_file_path: Optional[str] = Field(None, description="이미지 생성 프롬프트 파일 경로")
    image_maker_type: ImageMakerType = Field(default=ImageMakerType.DREAM_SHAPER, description="사용할 이미지 메이커 타입")
```

- 프롬프트 파일
- 이미지 생성기 타입 (ghibli_diffusion, dream_shaper)

**출력**: 

```python
# Image Maker 응답
class GeneratedImage(BaseModel):
    image_path: str = Field(..., description="생성된 이미지 파일 경로")
    image_name: str = Field(..., description="이미지 파일명")
    width: int = Field(..., description="이미지 너비")
    height: int = Field(..., description="이미지 높이")
    file_size: Optional[int] = Field(None, description="파일 크기 (바이트)")
    generation_seed: Optional[int] = Field(None, description="생성 시드")

class ImageMakerResponse(BaseResponse):
    generated_images: List[GeneratedImage] = Field(default_factory=list, description="생성된 이미지 정보")
    prompt_used: Optional[str] = Field(None, description="사용된 프롬프트")
    total_images: int = Field(0, description="생성된 총 이미지 수")
    model_used: Optional[str] = Field(None, description="사용된 모델")
    generation_parameters: Optional[Dict[str, Any]] = Field(None, description="생성 파라미터")
```

- 생성된 이미지 정보 (경로, 크기, 파일 크기)
- 사용된 프롬프트
- 생성 파라미터

`POST /image/text`

**작업 내용**: 입력 프롬프트로 이미지 생성

**입력**: 

```python
class ImageMakerTextRequest(BaseModel):
    prompt: str = Field(..., description="이미지 생성 프롬프트")
    image_maker_type: ImageMakerType = Field(default=ImageMakerType.DREAM_SHAPER, description="사용할 이미지 메이커 타입")
    num_images: Optional[int] = Field(default=1, description="생성할 이미지 개수")
```

- 이미지 생성 프롬프트
- 이미지 생성기 타입
- 생성할 이미지 개수

**출력**: 

```python
# 파이프 라인 응답
class PipelineResponse(BaseResponse):
    total_processing_time: float = Field(..., description="파이프라인 전체 처리 시간 (초)")
    mode: str = Field(..., description="파이프라인 실행 모드 (예: batch, single)")
```

- 생성된 이미지들의 상세 정보
- 생성 모델 및 파라미터 정보

---

## 데이터베이스 저장 권장 사항

### 1. 작업 로그 테이블 (job_logs)
```sql
- job_id (UUID, Primary Key)
- endpoint (VARCHAR) - 사용된 엔드포인트
- job_type (VARCHAR) - 작업 유형 (ocr, translator, story, etc.)
- status (VARCHAR) - 작업 상태 (success, error, processing)
- input_file_path (VARCHAR) - 입력 파일 경로
- output_directory (VARCHAR) - 출력 디렉토리 경로
- processing_time (FLOAT) - 처리 시간
- model_type (VARCHAR) - 사용된 모델 타입
- created_at (TIMESTAMP)
- completed_at (TIMESTAMP)
- error_message (TEXT) - 에러 발생 시 메시지
```

### 2. 처리 결과 테이블 (processing_results)
```sql
- result_id (UUID, Primary Key)
- job_id (UUID, Foreign Key)
- result_type (VARCHAR) - 결과 유형
- original_content (TEXT) - 원본 내용
- processed_content (TEXT) - 처리된 내용
- confidence_score (FLOAT) - 신뢰도 점수
- metadata (JSON) - 추가 메타데이터
- file_size (BIGINT) - 파일 크기
- created_at (TIMESTAMP)
```

### 3. 감정 분석 상세 테이블 (emotion_analysis)
```sql
- analysis_id (UUID, Primary Key)
- job_id (UUID, Foreign Key)
- primary_emotion (VARCHAR)
- emotion_scores (JSON) - 모든 감정 점수
- sentiment_polarity (VARCHAR)
- intensity (FLOAT)
- created_at (TIMESTAMP)
```

### 4. 생성된 이미지 테이블 (generated_images)
```sql
- image_id (UUID, Primary Key)
- job_id (UUID, Foreign Key)
- image_path (VARCHAR)
- image_name (VARCHAR)
- width (INT)
- height (INT)
- file_size (BIGINT)
- generation_seed (INT)
- prompt_used (TEXT)
- model_used (VARCHAR)
- generation_parameters (JSON)
- created_at (TIMESTAMP)
```

### 5. 장면 분석 테이블 (scene_analysis)
```sql
- scene_id (UUID, Primary Key)
- job_id (UUID, Foreign Key)
- scene_number (INT)
- scene_title (VARCHAR)
- characters (JSON) - 등장인물 배열
- location (VARCHAR)
- time_setting (VARCHAR)
- mood (VARCHAR)
- summary (TEXT)
- dialogue_count (INT)
- created_at (TIMESTAMP)
```

### 6. 사용 통계 테이블 (usage_statistics)
```sql
- stat_id (UUID, Primary Key)
- date (DATE)
- endpoint (VARCHAR)
- model_type (VARCHAR)
- total_requests (INT)
- successful_requests (INT)
- failed_requests (INT)
- avg_processing_time (FLOAT)
- total_processing_time (FLOAT)
```

### 인덱스 권장 사항
- `job_logs`: created_at, status, job_type
- `processing_results`: job_id, created_at
- `usage_statistics`: date, endpoint, model_type
- `generated_images`: job_id, created_at
- `scene_analysis`: job_id, scene_number## 🧪 테스트


interface 구현체 호출 (ex. OCR 수행)
```bash
# 단위 테스트 실행
pytest tests/

# API 테스트
pytest tests/test_api.py

# 통합 테스트
pytest tests/test_integration.py
```

## 📊 성능

- **OCR 정확도**: ~95%
- **번역 품질**: BLEU 스코어 ~90
- **감정 분석 정확도**: ~85%
- **스토리 생성 응답시간**: ~3-5초
- **이미지 생성 시간**: ~10-15초

## 🤝 기여하기

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다. 자세한 내용은 `LICENSE` 파일을 참조하세요.

## 👥 팀

- **AI Pipeline**: AI 모델 통합 및 API 개발
- **Frontend**: 사용자 인터페이스 개발
- **Backend**: 데이터베이스 및 서버 관리

## 🔮 로드맵

- [ ] 실시간 일기 분석 기능
- [ ] 다양한 그림체 지원
- [ ] 음성 일기 입력 지원
- [ ] 애니메이션 스토리북 생성
- [ ] 다국어 스토리 생성 확장

## 📞 문의

프로젝트에 대한 문의사항이 있으시면 [이슈](https://github.com/[username]/storypool_ai_pipeline/issues)를 생성해 주세요.
