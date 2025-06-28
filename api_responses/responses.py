from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from enum import Enum

# 공통 상태 코드
class StatusCode(str, Enum):
    SUCCESS = "success"
    ERROR = "error"
    PROCESSING = "processing"
    PARTIAL_SUCCESS = "partial_success"

# 기본 응답 모델 (output_directory 추가)
class BaseResponse(BaseModel):
    status: StatusCode = Field(..., description="처리 상태")
    message: str = Field(..., description="응답 메시지")
    timestamp: datetime = Field(default_factory=datetime.now, description="응답 시간")
    processing_time: Optional[float] = Field(None, description="처리 시간 (초)")
    output_directory: Optional[str] = Field(None, description="결과 출력 디렉토리 경로")

# OCR 응답
class OCRResponse(BaseResponse):
    extracted_text: Optional[str] = Field(None, description="추출된 텍스트")
    confidence_score: Optional[float] = Field(None, description="인식 신뢰도 점수")
    detected_languages: Optional[List[str]] = Field(None, description="감지된 언어 목록")
    bounding_boxes: Optional[List[Dict[str, Any]]] = Field(None, description="텍스트 영역 좌표 정보")

class OCRBatchResponse(BaseResponse):
    results: List[Dict[str, Union[str, float, List]]] = Field(default_factory=list, description="배치 처리 결과")
    total_processed: int = Field(0, description="처리된 총 이미지 수")
    successful_count: int = Field(0, description="성공한 처리 개수")
    failed_count: int = Field(0, description="실패한 처리 개수")

# Translator 응답
class TranslatorResponse(BaseResponse):
    original_text: Optional[str] = Field(None, description="원본 텍스트")
    translated_text: Optional[str] = Field(None, description="번역된 텍스트")
    source_language: Optional[str] = Field(None, description="원본 언어")
    target_language: Optional[str] = Field(None, description="대상 언어")
    confidence_score: Optional[float] = Field(None, description="번역 신뢰도")

# Story Writer 응답
class StoryWriterResponse(BaseResponse):
    generated_story: Optional[str] = Field(None, description="생성된 스토리")
    genre: Optional[str] = Field(None, description="감지된 장르")
    writing_style: Optional[str] = Field(None, description="작성 스타일")

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

# Prompt Maker 응답
class PromptMakerResponse(BaseResponse):
    generated_prompt: Optional[str] = Field(None, description="생성된 프롬프트")
    prompt_type: Optional[str] = Field(None, description="프롬프트 유형")
    keywords: List[str] = Field(default_factory=list, description="추출된 키워드")
    estimated_length: Optional[int] = Field(None, description="예상 응답 길이")
    prompt_quality_score: Optional[float] = Field(None, description="프롬프트 품질 점수")

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

class EmotionClassifierBatchResponse(BaseResponse):
    results: Dict[str, Dict[str, Any]] = Field(default_factory=dict, description="배치 처리 결과")
    summary: Dict[str, Any] = Field(default_factory=dict, description="전체 감정 분석 요약")
    total_processed: int = Field(0, description="처리된 총 파일 수")

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

# 파이프 라인 응답
class PipelineResponse(BaseResponse):
    total_processing_time: float = Field(..., description="파이프라인 전체 처리 시간 (초)")
    mode: str = Field(..., description="파이프라인 실행 모드 (예: batch, single)")

# 에러 응답
class ErrorDetail(BaseModel):
    error_code: str = Field(..., description="에러 코드")
    error_type: str = Field(..., description="에러 유형")
    description: str = Field(..., description="에러 설명")
    suggestion: Optional[str] = Field(None, description="해결 방안 제안")

class ErrorResponse(BaseResponse):
    error_details: ErrorDetail = Field(..., description="상세 에러 정보")
    stack_trace: Optional[str] = Field(None, description="스택 트레이스 (디버그용)")

# 헬스 체크 응답
class HealthCheckResponse(BaseModel):
    status: str = Field(..., description="서비스 상태")
    version: str = Field(..., description="API 버전")
    uptime: float = Field(..., description="서비스 가동 시간 (초)")
    components: Dict[str, str] = Field(default_factory=dict, description="각 컴포넌트 상태")
    timestamp: datetime = Field(default_factory=datetime.now, description="체크 시간")

# 작업 상태 응답 (비동기 처리용)
class TaskStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class TaskResponse(BaseModel):
    task_id: str = Field(..., description="작업 ID")
    status: TaskStatus = Field(..., description="작업 상태")
    progress: Optional[float] = Field(None, description="진행률 (0-100)")
    created_at: datetime = Field(default_factory=datetime.now, description="작업 생성 시간")
    started_at: Optional[datetime] = Field(None, description="작업 시작 시간")
    completed_at: Optional[datetime] = Field(None, description="작업 완료 시간")
    result: Optional[Dict[str, Any]] = Field(None, description="작업 결과")
    error: Optional[str] = Field(None, description="에러 메시지")