from sqlalchemy import create_engine, Column, String, DateTime, Text, Integer, LargeBinary, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

Base = declarative_base()

class PipelineExecution(Base):
    __tablename__ = "pipeline_executions"
    
    pipeline_id = Column(String(50), primary_key=True)
    status = Column(String(20), nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime)
    total_processing_time = Column(Float)
    config = Column(Text)  # JSON string
    error_message = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

class PipelineStep(Base):
    __tablename__ = "pipeline_steps"
    
    id = Column(String(50), primary_key=True)
    step_order = Column(Integer, nullable=False)
    status = Column(String(20), nullable=False)
    processing_time = Column(Float)
    error_message = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

class PipelineFile(Base):
    __tablename__ = "pipeline_files"
    
    id = Column(String(50), primary_key=True)
    pipeline_id = Column(String(50), nullable=False)
    step_order = Column(Integer, nullable=False)
    file_content = Column(LargeBinary)  # For binary files
    file_text = Column(Text)  # For text files
    created_at = Column(DateTime, default=datetime.utcnow)

class DatabaseEngine:
    """Database engine and session management"""
    
    def __init__(self, database_url: str):
        self.engine = create_engine(database_url)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        Base.metadata.create_all(bind=self.engine)
    
    def get_session(self):
        return self.SessionLocal()