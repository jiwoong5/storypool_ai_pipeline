import json
from typing import List, Optional
from sqlalchemy.orm import Session
from datetime import datetime
from .pipeline_models import PipelineExecution, PipelineStep, PipelineFile, DatabaseEngine
from constants.configs.configs import PipelineConfig

class PipelineCRUD:
    """CRUD operations for pipeline data"""
    
    def __init__(self, database_url: str):
        self.db_engine = DatabaseEngine(database_url)
    
    def get_session(self) -> Session:
        return self.db_engine.get_session()
    
    # Pipeline Execution CRUD
    def create_pipeline_execution(self, pipeline_id: str, config: PipelineConfig, status: str = "RUNNING") -> PipelineExecution:
        """Create a new pipeline execution record"""
        with self.get_session() as session:
            execution = PipelineExecution(
                pipeline_id=pipeline_id,
                status=status,
                start_time=datetime.utcnow(),
                config=json.dumps(config.__dict__)
            )
            session.add(execution)
            session.commit()
            return execution
    
    def get_pipeline_execution(self, pipeline_id: str) -> Optional[PipelineExecution]:
        """Get pipeline execution by ID"""
        with self.get_session() as session:
            return session.query(PipelineExecution).filter_by(pipeline_id=pipeline_id).first()
    
    def update_pipeline_execution(self, pipeline_id: str, status: str, total_time: float = None, error_message: str = None) -> bool:
        """Update pipeline execution status and completion info"""
        with self.get_session() as session:
            execution = session.query(PipelineExecution).filter_by(pipeline_id=pipeline_id).first()
            if execution:
                execution.status = status
                execution.end_time = datetime.utcnow()
                if total_time:
                    execution.total_processing_time = total_time
                if error_message:
                    execution.error_message = error_message
                session.commit()
                return True
            return False
    
    def get_all_pipeline_executions(self, limit: int = 100) -> List[PipelineExecution]:
        """Get all pipeline executions with limit"""
        with self.get_session() as session:
            return session.query(PipelineExecution).order_by(PipelineExecution.created_at.desc()).limit(limit).all()
    
    def delete_pipeline_execution(self, pipeline_id: str) -> bool:
        """Delete pipeline execution and all related data"""
        with self.get_session() as session:
            # Delete related files
            session.query(PipelineFile).filter_by(pipeline_id=pipeline_id).delete()
            # Delete related steps
            session.query(PipelineStep).filter_by(pipeline_id=pipeline_id).delete()
            # Delete execution
            execution = session.query(PipelineExecution).filter_by(pipeline_id=pipeline_id).first()
            if execution:
                session.delete(execution)
                session.commit()
                return True
            return False
    
    # Pipeline Step CRUD
    def create_pipeline_step(self, step_id: str, pipeline_id: str, step_name: str, step_order: int, 
                            status: str, processing_time: float = None, input_data: str = None, 
                            output_data: str = None, error_message: str = None) -> PipelineStep:
        """Create a new pipeline step record"""
        with self.get_session() as session:
            step = PipelineStep(
                id=step_id,
                pipeline_id=pipeline_id,
                step_name=step_name,
                step_order=step_order,
                status=status,
                processing_time=processing_time,
                input_data=input_data,
                output_data=output_data,
                error_message=error_message
            )
            session.add(step)
            session.commit()
            return step
    
    def get_pipeline_step(self, step_id: str) -> Optional[PipelineStep]:
        """Get pipeline step by ID"""
        with self.get_session() as session:
            return session.query(PipelineStep).filter_by(id=step_id).first()
    
    def get_pipeline_steps(self, pipeline_id: str) -> List[PipelineStep]:
        """Get all steps for a pipeline"""
        with self.get_session() as session:
            return session.query(PipelineStep).filter_by(pipeline_id=pipeline_id).order_by(PipelineStep.step_order).all()
    
    def update_pipeline_step(self, step_id: str, status: str, processing_time: float = None, 
                            output_data: str = None, error_message: str = None) -> bool:
        """Update pipeline step status and results"""
        with self.get_session() as session:
            step = session.query(PipelineStep).filter_by(id=step_id).first()
            if step:
                step.status = status
                if processing_time:
                    step.processing_time = processing_time
                if output_data:
                    step.output_data = output_data
                if error_message:
                    step.error_message = error_message
                session.commit()
                return True
            return False
    
    def delete_pipeline_step(self, step_id: str) -> bool:
        """Delete pipeline step and related files"""
        with self.get_session() as session:
            # Delete related files
            session.query(PipelineFile).filter_by(step_id=step_id).delete()
            # Delete step
            step = session.query(PipelineStep).filter_by(id=step_id).first()
            if step:
                session.delete(step)
                session.commit()
                return True
            return False
    
    # Pipeline File CRUD
    def create_pipeline_file(self, file_id: str, pipeline_id: str, step_id: str, file_name: str, 
                            file_type: str, file_content: bytes = None, file_text: str = None) -> PipelineFile:
        """Create a new pipeline file record"""
        with self.get_session() as session:
            file_record = PipelineFile(
                id=file_id,
                pipeline_id=pipeline_id,
                step_id=step_id,
                file_name=file_name,
                file_type=file_type,
                file_content=file_content,
                file_text=file_text
            )
            session.add(file_record)
            session.commit()
            return file_record
    
    def get_pipeline_file(self, file_id: str) -> Optional[PipelineFile]:
        """Get pipeline file by ID"""
        with self.get_session() as session:
            return session.query(PipelineFile).filter_by(id=file_id).first()
    
    def get_file_content(self, file_id: str) -> Optional[bytes]:
        """Get file content by file ID"""
        with self.get_session() as session:
            file_record = session.query(PipelineFile).filter_by(id=file_id).first()
            return file_record.file_content if file_record else None
    
    def get_file_text(self, file_id: str) -> Optional[str]:
        """Get file text by file ID"""
        with self.get_session() as session:
            file_record = session.query(PipelineFile).filter_by(id=file_id).first()
            return file_record.file_text if file_record else None
    
    def get_pipeline_files(self, pipeline_id: str, file_type: str = None, step_id: str = None) -> List[PipelineFile]:
        """Get files for a pipeline, optionally filtered by type or step"""
        with self.get_session() as session:
            query = session.query(PipelineFile).filter_by(pipeline_id=pipeline_id)
            if file_type:
                query = query.filter_by(file_type=file_type)
            if step_id:
                query = query.filter_by(step_id=step_id)
            return query.order_by(PipelineFile.created_at).all()
    
    def get_pipeline_images(self, pipeline_id: str) -> List[PipelineFile]:
        """Get all image files for a pipeline"""
        return self.get_pipeline_files(pipeline_id, file_type="image")
    
    def update_pipeline_file(self, file_id: str, file_content: bytes = None, file_text: str = None) -> bool:
        """Update pipeline file content"""
        with self.get_session() as session:
            file_record = session.query(PipelineFile).filter_by(id=file_id).first()
            if file_record:
                if file_content is not None:
                    file_record.file_content = file_content
                if file_text is not None:
                    file_record.file_text = file_text
                session.commit()
                return True
            return False
    
    def delete_pipeline_file(self, file_id: str) -> bool:
        """Delete pipeline file"""
        with self.get_session() as session:
            file_record = session.query(PipelineFile).filter_by(id=file_id).first()
            if file_record:
                session.delete(file_record)
                session.commit()
                return True
            return False
    
    def delete_pipeline_files(self, pipeline_id: str, file_type: str = None) -> int:
        """Delete multiple pipeline files, optionally filtered by type"""
        with self.get_session() as session:
            query = session.query(PipelineFile).filter_by(pipeline_id=pipeline_id)
            if file_type:
                query = query.filter_by(file_type=file_type)
            count = query.count()
            query.delete()
            session.commit()
            return count
    
    # Utility methods
    def get_pipeline_summary(self, pipeline_id: str) -> dict:
        """Get summary information about a pipeline"""
        with self.get_session() as session:
            execution = session.query(PipelineExecution).filter_by(pipeline_id=pipeline_id).first()
            if not execution:
                return None
            
            steps = session.query(PipelineStep).filter_by(pipeline_id=pipeline_id).order_by(PipelineStep.step_order).all()
            files = session.query(PipelineFile).filter_by(pipeline_id=pipeline_id).all()
            
            return {
                "pipeline_id": pipeline_id,
                "status": execution.status,
                "start_time": execution.start_time,
                "end_time": execution.end_time,
                "total_processing_time": execution.total_processing_time,
                "error_message": execution.error_message,
                "steps_count": len(steps),
                "files_count": len(files),
                "image_count": len([f for f in files if f.file_type == "image"]),
                "steps": [
                    {
                        "step_name": step.step_name,
                        "status": step.status,
                        "processing_time": step.processing_time,
                        "error_message": step.error_message
                    }
                    for step in steps
                ]
            }
    
    def cleanup_old_pipelines(self, days_old: int = 30) -> int:
        """Clean up pipelines older than specified days"""
        from datetime import timedelta
        
        cutoff_date = datetime.utcnow() - timedelta(days=days_old)
        
        with self.get_session() as session:
            # Get old pipelines
            old_pipelines = session.query(PipelineExecution).filter(
                PipelineExecution.created_at < cutoff_date
            ).all()
            
            count = 0
            for pipeline in old_pipelines:
                # Delete related files
                session.query(PipelineFile).filter_by(pipeline_id=pipeline.pipeline_id).delete()
                # Delete related steps
                session.query(PipelineStep).filter_by(pipeline_id=pipeline.pipeline_id).delete()
                # Delete execution
                session.delete(pipeline)
                count += 1
            
            session.commit()
            return count