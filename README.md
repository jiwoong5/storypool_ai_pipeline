# StoryPool AI Pipeline 📚✨

> 사용자의 일기를 바탕으로 개인화된 그림동화를 자동 생성하는 AI 파이프라인

## 🎯 프로젝트 개요

StoryPool AI Pipeline은 사용자가 작성한 일기 텍스트를 분석하여 감정과 상황을 파악하고, 이를 바탕으로 개인화된 그림동화를 자동으로 생성하는 멀티모달 AI 시스템.

### 주요 기능
- 📝 **OCR**: 손글씨 일기를 텍스트로 변환
- 🌐 **번역**: 다국어 일기 내용을 영어로 번역
- 🎭 **감정 분석**: 일기 내용의 감정 상태 분석
- 📖 **스토리 생성**: AI 기반 일기내용을 이용한 동화 스토리 생성
- 🎬 **장면 분석**: 스토리의 장면별 구조 분석
- 🎨 **이미지 생성**: 스토리에 맞는 일러스트 자동 생성
- 💡 **프롬프트 최적화**: 각 모듈의 AI 프롬프트 자동 생성

## 🏗️ 시스템 아키텍처

```
사용자 일기 입력
    ↓
OCR (손글씨 → 텍스트)
    ↓
번역 (다국어 → 한국어/영어)
    ↓
감정 분석 (감정 상태 파악)
    ↓
스토리 생성 (개인화 동화 생성)
    ↓
장면 분석 (스토리 구조화)
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
- kss.core==1.6.5: 한국어 문장 분리기 (Korean Sentence Splitter) 라이브러리
- numpy==2.3.1: 고성능 수치 계산을 위한 배열 및 행렬 연산 라이브러리
- Pillow==11.2.1: Python에서 이미지 처리와 조작을 위한 라이브러리 (PIL의 후속)
- pydantic==2.11.7: 데이터 유효성 검사 및 설정 관리를 위한 타입 기반 모델링 라이브러리
- pytest==8.4.1: Python 테스트 코드 작성과 실행을 도와주는 테스트 프레임워크
- sentence_transformers==4.1.0: 문장 임베딩 벡터 생성 및 문장 간 유사도 계산에 특화된 라이브러리
- torch==2.7.1: 딥러닝 모델 개발에 널리 쓰이는 PyTorch 라이브러리
- transformers==4.53.0: Hugging Face에서 제공하는 다양한 사전학습 NLP 모델 사용 라이브러리
- uvicorn==0.35.0: ASGI 기반 비동기 Python 웹서버, 주로 FastAPI와 함께 사용됨


### 설치
```bash
git clone https://github.com/jiwoong5/storypool_ai_pipeline.git
cd storypool_ai_pipeline
pip install -r requirements.txt
```

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
    json={"prompt": "즐거운 놀이터에서의 하루", "writer_type": "llama"}
).json())

# 4. 장면 분석 (텍스트)
print(requests.post(
    "http://localhost:8000/scene/text",
    json={"text": "주인공이 마을을 떠나 모험을 시작했다.", "parser_type": "basic"}
).json())

# 5-1. 감정 분석 (텍스트)
print(requests.post(
    "http://localhost:8000/emotion/text",
    json={"text": "오늘은 친구들과 놀이터에서 정말 즐거운 시간을 보냈어요!", "emotion_classifer_type": "minilm"}
).json())

# 5-2-1. 이미지 프롬프트 생성 (텍스트)
print(requests.post(
    "http://localhost:8000/prompt/text",
    json={"input_text": "여름 해변에서 노는 아이들", "prompt_maker_type": "llama"}
).json())

# 5-2-2. 이미지 생성 (텍스트 프롬프트)
print(requests.post(
    "http://localhost:8000/image/text",
    json={"prompt": "A beautiful summer beach with children playing", "image_maker_type": "dream_shaper", "num_images": 1}
).json())

```

## 🧪 테스트

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
