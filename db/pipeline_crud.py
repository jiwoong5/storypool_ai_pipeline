from sqlalchemy.orm import Session
from datetime import datetime
from .pipeline_models import PipelineResult, DatabaseEngine

class PipelineCRUD:
    """CRUD operations for pipeline data"""
    
    def __init__(self, database_url: str):
        self.db_engine = DatabaseEngine(database_url)
    
    def get_session(self) -> Session:
        return self.db_engine.get_session()

    def save_scene_image(
        self,
        db: Session,
        pipeline_id: str,
        scene_number: int,
        image_bytes: bytes
    ) -> None:
        """
        Save or update a scene image identified by (pipeline_id, scene_number).
        """
        result = (
            db.query(PipelineResult)
            .filter_by(pipeline_id=pipeline_id, scene_number=scene_number)
            .first()
        )

        now = datetime.utcnow()

        if result:
            result.scene_image = image_bytes
            result.updated_at = now  # If you use updated_at
        else:
            result = PipelineResult(
                pipeline_id=pipeline_id,
                scene_number=scene_number,
                scene_image=image_bytes,
                created_at=now
            )
            db.add(result)

        db.commit()
