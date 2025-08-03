from sqlalchemy import create_engine, Column, String, DateTime, Text, Integer, LargeBinary, PrimaryKeyConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

Base = declarative_base()

class PipelineResult(Base):
    __tablename__ = "pipeline_result"

    pipeline_id = Column(String(64), nullable=False)
    scene_number = Column(Integer, nullable=False)
    mood = Column(String(50), nullable=True)
    scene_story = Column(Text, nullable=True)
    scene_image = Column(LargeBinary, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        PrimaryKeyConstraint('pipeline_id', 'scene_number', name='pipeline_scene_pk'),
    )

class DatabaseEngine:
    """Database engine and session management"""

    def __init__(self, database_url: str):
        self.engine = create_engine(database_url)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        Base.metadata.create_all(bind=self.engine)

    def get_session(self):
        return self.SessionLocal()
