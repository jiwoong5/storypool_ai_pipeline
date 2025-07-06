from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum

# Pipeline Status Enum
class PipelineStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PARTIAL_SUCCESS = "partial_success"

# Pipeline Step Status
class StepStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"

# Pipeline Step Result
@dataclass
class StepResult:
    step_name: str
    status: StepStatus
    processing_time: float
    output_data: Optional[Any] = None
    error_message: Optional[str] = None
    output_files: Optional[List[str]] = None

# Pipeline Result
@dataclass
class PipelineResult:
    pipeline_id: str
    status: PipelineStatus
    total_processing_time: float
    output_directory: str
    steps: List[StepResult]
    final_images: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None