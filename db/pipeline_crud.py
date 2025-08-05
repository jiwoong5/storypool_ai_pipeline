from sqlalchemy.orm import Session
from datetime import datetime
from .pipeline_models import PipelineResult, DatabaseEngine

class PipelineCRUD:
    """CRUD operations for pipeline data"""
    
    def __init__(self, database_url: str):
        self.db_engine = DatabaseEngine(database_url)
    
    def get_session(self) -> Session:
        return self.db_engine.get_session()

    def save_scene_image_url(
        self,
        db: Session,
        pipeline_id: str,
        scene_number: int,
        image_url: str
    ) -> None:
        
        result = (
            db.query(PipelineResult)
            .filter_by(pipeline_id=pipeline_id, scene_number=scene_number)
            .first()
        )

        now = datetime.utcnow()

        if result:
            result.scene_image_url = image_url
        else:
            result = PipelineResult(
                pipeline_id=pipeline_id,
                scene_number=scene_number,
                scene_image_url=image_url,
                created_at=now
            )
            db.add(result)

        db.commit()

    def save_scene_story(
        self,
        db: Session,
        pipeline_id: str,
        scene_number: int,
        scene_story: str
    ) -> None:
        """
        Save or update a scene story (Korean translation) identified by (pipeline_id, scene_number).
        """
        result = (
            db.query(PipelineResult)
            .filter_by(pipeline_id=pipeline_id, scene_number=scene_number)
            .first()
        )

        now = datetime.utcnow()

        if result:
            result.scene_story = scene_story
        else:
            result = PipelineResult(
                pipeline_id=pipeline_id,
                scene_number=scene_number,
                scene_story=scene_story,
                created_at=now
            )
            db.add(result)

        db.commit()
    
    def save_mood(
            
        self,
        db: Session,
        pipeline_id: str,
        scene_number: int,
        mood: str
    ) -> None:
        """
        Save or update the mood for a given scene.
        """
        result = (
            db.query(PipelineResult)
            .filter_by(pipeline_id=pipeline_id, scene_number=scene_number)
            .first()
        )

        now = datetime.utcnow()

        if result:
            result.mood = mood
        else:
            result = PipelineResult(
                pipeline_id=pipeline_id,
                scene_number=scene_number,
                mood=mood,
                created_at=now
            )
            db.add(result)

        db.commit()
        
    def get_result_payload(self, db: Session, pipeline_id: str) -> dict:
        """
        특정 pipeline_id에 해당하는 전체 scene 결과를 조회하여 payload 형식으로 반환
        """
        results = (
            db.query(PipelineResult)
            .filter_by(pipeline_id=pipeline_id)
            .order_by(PipelineResult.scene_number)
            .all()
        )

        page_list = [
            {
                "pageIndex": result.scene_number,
                "mood": result.mood,
                "story": result.scene_story,
                "imageUrl": result.scene_image_url
            }
            for result in results
        ]

        return {
            "pipelineId": pipeline_id,
            "status": "completed",
            "pageList": page_list
        }