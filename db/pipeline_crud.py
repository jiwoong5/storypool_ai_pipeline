import json
from typing import List, Optional
from sqlalchemy.orm import Session
from datetime import datetime

from .pipeline_models import PipelineExecution, PipelineStep, PipelineFile, PipelineResult, DatabaseEngine
from constants.configs.configs import PipelineConfig

class PipelineCRUD:
    """CRUD operations for pipeline data"""
    
    def __init__(self, database_url: str):
        self.db_engine = DatabaseEngine(database_url)
    
    def get_session(self) -> Session:
        return self.db_engine.get_session()
    
    def save_scene_image(self, db: Session, pipeline_id: str, scene_number: int, image_bytes: bytes):
        """
        pipeline_id와 scene_number를 기준으로 이미지 저장 또는 업데이트.
        """
        result = db.query(PipelineResult).filter_by(id=pipeline_id, scene_number=scene_number).first()

        if result:
            result.scene_image = image_bytes
            result.created_at = datetime.utcnow()
        else:
            result = PipelineResult(
                id=pipeline_id,
                scene_number=scene_number,
                scene_image=image_bytes,
                created_at=datetime.utcnow()
            )
            db.add(result)

        db.commit()
