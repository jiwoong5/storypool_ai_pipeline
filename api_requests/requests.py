from pydantic import BaseModel, Field
from typing import Optional, List, Union
from enum import Enum

# Enum 정의
class OCRReaderType(str, Enum):
    EASYOCR = "easyocr"

class TranslatorType(str, Enum):
    MARIN = "marin"
    NLLB = "nllb"

class StoryWriterType(str, Enum):
    LLAMA = "llama"
    GPT = "gpt"
    CLAUDE = "claude"

class SceneParserType(str, Enum):
    BASIC = "basic"
    ADVANCED = "advanced"
    CUSTOM = "custom"

class PromptMakerType(str, Enum):
    LLAMA = "llama"
    GPT = "gpt"
    CLAUDE = "claude"

class ImageMakerType(str, Enum):
    DREAM_SHAPER = "dream_shaper"
    STABLE_DIFFUSION = "stable_diffusion"
    DALL_E = "dall_e"

# OCR 요청
class OCRRequest(BaseModel):
    image_path: str = Field(..., description="처리할 이미지 파일 경로")
    reader_type: OCRReaderType = Field(default=OCRReaderType.EASYOCR, description="사용할 OCR 리더 타입")
    
class OCRBatchRequest(BaseModel):
    image_paths: List[str] = Field(..., description="처리할 이미지 파일 경로 리스트")
    reader_type: OCRReaderType = Field(default=OCRReaderType.EASYOCR, description="사용할 OCR 리더 타입")

# Translator 요청
class TranslatorRequest(BaseModel):
    input_file_path: str = Field(..., description="번역할 텍스트 파일 경로")
    output_file_path: str = Field(..., description="번역 결과를 저장할 파일 경로")
    language_pair: str = Field(..., description="언어 쌍 (예: 'en-ko', 'ko-en')")
    translator_type: TranslatorType = Field(default=TranslatorType.GOOGLE, description="사용할 번역기 타입")

class TranslatorTextRequest(BaseModel):
    text: str = Field(..., description="번역할 텍스트")
    language_pair: str = Field(..., description="언어 쌍 (예: 'en-ko', 'ko-en')")
    translator_type: TranslatorType = Field(default=TranslatorType.GOOGLE, description="사용할 번역기 타입")

# Story Writer 요청
class StoryWriterRequest(BaseModel):
    input_file_path: str = Field(..., description="스토리 작성 입력 파일 경로")
    output_file_path: str = Field(..., description="스토리 결과를 저장할 파일 경로")
    writer_type: StoryWriterType = Field(default=StoryWriterType.LLAMA, description="사용할 스토리 라이터 타입")

class StoryWriterTextRequest(BaseModel):
    prompt: str = Field(..., description="스토리 작성 프롬프트")
    writer_type: StoryWriterType = Field(default=StoryWriterType.LLAMA, description="사용할 스토리 라이터 타입")

# Scene Parser 요청
class SceneParserRequest(BaseModel):
    input_file_path: str = Field(..., description="장면 분석할 텍스트 파일 경로")
    output_file_path: str = Field(..., description="장면 분석 결과를 저장할 파일 경로")
    parser_type: SceneParserType = Field(default=SceneParserType.BASIC, description="사용할 장면 파서 타입")

class SceneParserTextRequest(BaseModel):
    text: str = Field(..., description="장면 분석할 텍스트")
    parser_type: SceneParserType = Field(default=SceneParserType.BASIC, description="사용할 장면 파서 타입")

# Prompt Maker 요청
class PromptMakerRequest(BaseModel):
    input_file_path: str = Field(..., description="프롬프트 생성 입력 파일 경로")
    output_file_path: str = Field(..., description="프롬프트 결과를 저장할 파일 경로")
    prompt_maker_type: PromptMakerType = Field(default=PromptMakerType.LLAMA, description="사용할 프롬프트 메이커 타입")

class PromptMakerTextRequest(BaseModel):
    input_text: str = Field(..., description="프롬프트 생성을 위한 입력 텍스트")
    prompt_maker_type: PromptMakerType = Field(default=PromptMakerType.LLAMA, description="사용할 프롬프트 메이커 타입")

# Emotion Classifier 요청
class EmotionClassifierRequest(BaseModel):
    input_file_path: str = Field(..., description="감정 분류할 텍스트 파일 경로")
    output_file_path: str = Field(..., description="감정 분류 결과를 저장할 파일 경로")

class EmotionClassifierTextRequest(BaseModel):
    text: str = Field(..., description="감정 분류할 텍스트")

class EmotionClassifierBatchRequest(BaseModel):
    input_file_paths: List[str] = Field(..., description="감정 분류할 텍스트 파일 경로 리스트")
    output_dir: str = Field(..., description="감정 분류 결과를 저장할 디렉토리")

# Image Maker 요청
class ImageMakerRequest(BaseModel):
    input_file_path: str = Field(..., description="이미지 생성 프롬프트 파일 경로")
    output_dir: str = Field(..., description="생성된 이미지를 저장할 디렉토리")
    image_maker_type: ImageMakerType = Field(default=ImageMakerType.DREAM_SHAPER, description="사용할 이미지 메이커 타입")

class ImageMakerTextRequest(BaseModel):
    prompt: str = Field(..., description="이미지 생성 프롬프트")
    output_dir: str = Field(..., description="생성된 이미지를 저장할 디렉토리")
    image_maker_type: ImageMakerType = Field(default=ImageMakerType.DREAM_SHAPER, description="사용할 이미지 메이커 타입")
    width: Optional[int] = Field(default=512, description="이미지 너비")
    height: Optional[int] = Field(default=512, description="이미지 높이")
    num_images: Optional[int] = Field(default=1, description="생성할 이미지 개수")