import os
import json
import time
import uuid
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
from datetime import datetime
from fastapi import UploadFile
from sqlalchemy.orm import Session
from constants.configs.configs import PipelineConfig
from pipeline.pipeline_result import *
from db.pipeline_models import PipelineExecution, PipelineStep, PipelineFile, DatabaseEngine
from db.pipeline_crud import PipelineCRUD

# Import managers and selectors
from ocr.ocr_selector import OCRSelector
from ocr.ocr_manager import OCRManager
from translator.translator_selector import TranslatorSelector
from translator.translator_manager import TranslatorManager
from story_writer.story_writer_selector import StoryWriterSelector
from story_writer.story_writer_manager import StoryWriterManager
from scene_parser.scene_parser_selector import SceneParserSelector
from scene_parser.scene_parser_manager import SceneParserManager
from prompt_maker.prompt_maker_selector import PromptMakerSelector
from prompt_maker.prompt_maker_manager import PromptMakerManager
from image_maker.image_maker_selector import ImageMakerSelector
from image_maker.image_maker_manager import ImageMakerManager

# Main Pipeline Class
class AIProcessingPipeline:
    def __init__(self, config: PipelineConfig = None, db_engine: DatabaseEngine = None):
        self.config = config or PipelineConfig()
        self.db_engine = db_engine
        self.pipeline_id = None
        self.output_dir = None
        self.steps_results = []
        self.step_order = 0
        
    def generate_pipeline_id(self) -> str:
        """Generate unique pipeline ID"""
        return str(uuid.uuid4())
    
    def generate_step_id(self) -> str:
        """Generate unique step ID"""
        return str(uuid.uuid4())
    
    def save_pipeline_execution(self, db: Session, status: PipelineStatus, 
                               start_time: datetime, end_time: datetime = None,
                               total_processing_time: float = None, 
                               error_message: str = None) -> PipelineExecution:
        """Save or update pipeline execution in database"""
        crud = PipelineCRUD(db)
        
        # Check if pipeline exists
        existing_pipeline = crud.get_pipeline_execution(self.pipeline_id)
        
        if existing_pipeline:
            # Update existing pipeline
            update_data = {
                "status": status.value,
                "end_time": end_time,
                "total_processing_time": total_processing_time,
                "error_message": error_message
            }
            return crud.update_pipeline_execution(self.pipeline_id, update_data)
        else:
            # Create new pipeline
            pipeline_data = {
                "pipeline_id": self.pipeline_id,
                "status": status.value,
                "start_time": start_time,
                "end_time": end_time,
                "total_processing_time": total_processing_time,
                "config": json.dumps(self.config.__dict__),
                "error_message": error_message
            }
            return crud.create_pipeline_execution(pipeline_data)
    
    def save_pipeline_step(self, db: Session, step_result: StepResult, 
                          input_data: str = None) -> PipelineStep:
        """Save pipeline step in database"""
        crud = PipelineCRUD(db)
        
        step_data = {
            "id": self.generate_step_id(),
            "pipeline_id": self.pipeline_id,
            "step_name": step_result.step_name,
            "step_order": self.step_order,
            "status": step_result.status.value,
            "processing_time": step_result.processing_time,
            "input_data": input_data,
            "output_data": json.dumps(step_result.output_data) if step_result.output_data else None,
            "error_message": step_result.error_message
        }
        
        step = crud.create_pipeline_step(step_data)
        self.step_order += 1
        return step
    
    def save_pipeline_file(self, db: Session, step_id: str, file_name: str, 
                          file_type: str, file_content: bytes = None, 
                          file_text: str = None) -> PipelineFile:
        """Save pipeline file in database"""
        crud = PipelineCRUD(db)
        
        file_data = {
            "id": str(uuid.uuid4()),
            "pipeline_id": self.pipeline_id,
            "step_id": step_id,
            "file_name": file_name,
            "file_type": file_type,
            "file_content": file_content,
            "file_text": file_text
        }
        
        return crud.create_pipeline_file(file_data)
    
    async def run_from_file(self, file: UploadFile) -> PipelineResult:
        """Run complete pipeline from uploaded file"""
        start_time = datetime.utcnow()
        self.pipeline_id = self.generate_pipeline_id()
        self.step_order = 0
        
        db = self.db_engine.get_session() if self.db_engine else None
        
        try:
            # Initialize pipeline execution in database
            if db:
                self.save_pipeline_execution(db, PipelineStatus.RUNNING, start_time)
            
            # Step 1: OCR - Extract text from image
            ocr_result = await self._run_ocr_step(file, db)
            if ocr_result.status == StepStatus.FAILED and not self.config.continue_on_error:
                return self._create_failed_result(start_time, "OCR step failed", db)
            
            # Step 2: Translation - Translate extracted text
            translation_result = await self._run_translation_step(ocr_result.output_data, db)
            if translation_result.status == StepStatus.FAILED and not self.config.continue_on_error:
                return self._create_failed_result(start_time, "Translation step failed", db)
            
            # Step 3: Story Generation - Create story from translated text
            story_result = await self._run_story_step(translation_result.output_data, db)
            if story_result.status == StepStatus.FAILED and not self.config.continue_on_error:
                return self._create_failed_result(start_time, "Story generation step failed", db)
            
            # Step 4: Scene Parsing - Parse scenes from story
            scene_result = await self._run_scene_step(story_result.output_data, db)
            if scene_result.status == StepStatus.FAILED and not self.config.continue_on_error:
                return self._create_failed_result(start_time, "Scene parsing step failed", db)
            
            # Step 5: Prompt Generation - Generate prompts from scenes
            prompt_result = await self._run_prompt_step(scene_result.output_data, db)
            if prompt_result.status == StepStatus.FAILED and not self.config.continue_on_error:
                return self._create_failed_result(start_time, "Prompt generation step failed", db)
            
            # Step 6: Image Generation - Generate images from prompts
            image_result = await self._run_image_step(prompt_result.output_data, db)
            
            # Create final result
            end_time = datetime.utcnow()
            total_time = (end_time - start_time).total_seconds()
            pipeline_status = self._determine_pipeline_status()
            
            # Update pipeline execution in database
            if db:
                self.save_pipeline_execution(db, pipeline_status, start_time, end_time, total_time)
                db.commit()
            
            return PipelineResult(
                pipeline_id=self.pipeline_id,
                status=pipeline_status,
                total_processing_time=total_time,
                output_directory=self.output_dir or "",
                steps=self.steps_results,
                final_images=image_result.output_files if image_result.output_files else [],
                metadata={"config": self.config.__dict__}
            )
            
        except Exception as e:
            if db:
                db.rollback()
            return self._create_failed_result(start_time, f"Pipeline execution failed: {str(e)}", db)
        finally:
            if db:
                db.close()
    
    async def run_from_text(self, text: str) -> PipelineResult:
        """Run pipeline starting from text (skip OCR step)"""
        start_time = datetime.utcnow()
        self.pipeline_id = self.generate_pipeline_id()
        self.step_order = 0
        
        db = self.db_engine.get_session() if self.db_engine else None
        
        try:
            # Initialize pipeline execution in database
            if db:
                self.save_pipeline_execution(db, PipelineStatus.RUNNING, start_time)
            
            # Skip OCR, start from translation
            translation_result = await self._run_translation_step(text, db)
            if translation_result.status == StepStatus.FAILED and not self.config.continue_on_error:
                return self._create_failed_result(start_time, "Translation step failed", db)
            
            # Continue with remaining steps...
            story_result = await self._run_story_step(translation_result.output_data, db)
            scene_result = await self._run_scene_step(story_result.output_data, db)
            prompt_result = await self._run_prompt_step(scene_result.output_data, db)
            image_result = await self._run_image_step(prompt_result.output_data, db)
            
            end_time = datetime.utcnow()
            total_time = (end_time - start_time).total_seconds()
            pipeline_status = self._determine_pipeline_status()
            
            # Update pipeline execution in database
            if db:
                self.save_pipeline_execution(db, pipeline_status, start_time, end_time, total_time)
                db.commit()
            
            return PipelineResult(
                pipeline_id=self.pipeline_id,
                status=pipeline_status,
                total_processing_time=total_time,
                output_directory=self.output_dir or "",
                steps=self.steps_results,
                final_images=image_result.output_files if image_result.output_files else [],
                metadata={"config": self.config.__dict__}
            )
            
        except Exception as e:
            if db:
                db.rollback()
            return self._create_failed_result(start_time, f"Pipeline execution failed: {str(e)}", db)
        finally:
            if db:
                db.close()
    
    async def _run_ocr_step(self, file: UploadFile, db: Session = None) -> StepResult:
        """Run OCR step"""
        step_start = time.time()
        step_result = StepResult(step_name="OCR", status=StepStatus.RUNNING, processing_time=0)
        
        try:
            # Read uploaded file content
            file_content = await file.read()
            
            # Run OCR
            ocr_model = OCRSelector.get_reader(self.config.ocr_reader_type)
            ocr_manager = OCRManager(ocr_model)
            
            # Process OCR from file content
            extracted_text = ocr_manager.process(file_content)
            
            step_result.status = StepStatus.COMPLETED
            step_result.output_data = extracted_text
            
            # Save to database
            if db:
                step_db = self.save_pipeline_step(db, step_result)
                
                # Save input file
                self.save_pipeline_file(db, step_db.id, file.filename, "input", file_content)
                
                # Save output text
                self.save_pipeline_file(db, step_db.id, "ocr_result.txt", "output", 
                                      file_text=extracted_text)
            
        except Exception as e:
            step_result.status = StepStatus.FAILED
            step_result.error_message = str(e)
            
            if db:
                self.save_pipeline_step(db, step_result)
        
        step_result.processing_time = time.time() - step_start
        self.steps_results.append(step_result)
        return step_result
    
    async def _run_translation_step(self, input_text: str, db: Session = None) -> StepResult:
        """Run translation step"""
        step_start = time.time()
        step_result = StepResult(step_name="Translation", status=StepStatus.RUNNING, processing_time=0)
        
        try:
            # Run translation
            translator = TranslatorSelector.get_translator(self.config.translator_type)
            translator_manager = TranslatorManager(translator)
            
            translated_text = translator_manager.process(input_text)
            
            step_result.status = StepStatus.COMPLETED
            step_result.output_data = translated_text
            
            # Save to database
            if db:
                step_db = self.save_pipeline_step(db, step_result, input_text)
                
                # Save input and output
                self.save_pipeline_file(db, step_db.id, "translation_input.txt", "input", 
                                      file_text=input_text)
                self.save_pipeline_file(db, step_db.id, "translated.txt", "output", 
                                      file_text=translated_text)
            
        except Exception as e:
            step_result.status = StepStatus.FAILED
            step_result.error_message = str(e)
            # Use original text if translation fails
            step_result.output_data = input_text
            
            if db:
                self.save_pipeline_step(db, step_result, input_text)
        
        step_result.processing_time = time.time() - step_start
        self.steps_results.append(step_result)
        return step_result
    
    async def _run_story_step(self, input_text: str, db: Session = None) -> StepResult:
        """Run story generation step"""
        step_start = time.time()
        step_result = StepResult(step_name="Story Generation", status=StepStatus.RUNNING, processing_time=0)
        
        try:
            # Generate story
            story_writer = StoryWriterSelector.get_writer(self.config.story_writer_type)
            story_manager = StoryWriterManager(story_writer)
            
            generated_story = story_manager.process(input_text)
            
            step_result.status = StepStatus.COMPLETED
            step_result.output_data = generated_story
            
            # Save to database
            if db:
                step_db = self.save_pipeline_step(db, step_result, input_text)
                
                # Save input and output
                self.save_pipeline_file(db, step_db.id, "story_input.txt", "input", 
                                      file_text=input_text)
                self.save_pipeline_file(db, step_db.id, "story.txt", "output", 
                                      file_text=generated_story)
            
        except Exception as e:
            step_result.status = StepStatus.FAILED
            step_result.error_message = str(e)
            step_result.output_data = input_text  # Fallback to input
            
            if db:
                self.save_pipeline_step(db, step_result, input_text)
        
        step_result.processing_time = time.time() - step_start
        self.steps_results.append(step_result)
        return step_result
    
    async def _run_scene_step(self, story_text: str, db: Session = None) -> StepResult:
        """Run scene parsing step"""
        step_start = time.time()
        step_result = StepResult(step_name="Scene Parsing", status=StepStatus.RUNNING, processing_time=0)
        
        try:
            # Parse scenes
            scene_parser = SceneParserSelector.get_parser(self.config.scene_parser_type)
            scene_parser_manager = SceneParserManager(scene_parser)
            
            scene_response = scene_parser_manager.parse_scenes(story_text)
            
            step_result.status = StepStatus.COMPLETED
            step_result.output_data = scene_response
            
            # Save to database
            if db:
                step_db = self.save_pipeline_step(db, step_result, story_text)
                
                # Save input and output
                self.save_pipeline_file(db, step_db.id, "scene_input.txt", "input", 
                                      file_text=story_text)
                self.save_pipeline_file(db, step_db.id, "scenes.json", "output", 
                                      file_text=json.dumps(scene_response, indent=2))
            
        except Exception as e:
            step_result.status = StepStatus.FAILED
            step_result.error_message = str(e)
            step_result.output_data = None
            
            if db:
                self.save_pipeline_step(db, step_result, story_text)
        
        step_result.processing_time = time.time() - step_start
        self.steps_results.append(step_result)
        return step_result
    
    async def _run_prompt_step(self, scene_data: Any, db: Session = None) -> StepResult:
        """Run prompt generation step"""
        step_start = time.time()
        step_result = StepResult(step_name="Prompt Generation", status=StepStatus.RUNNING, processing_time=0)
        
        try:
            # Generate prompts
            prompt_maker = PromptMakerSelector.get_prompt_maker(self.config.prompt_maker_type)
            prompt_manager = PromptMakerManager(prompt_maker)
            
            prompt_result = prompt_manager.generate_prompts(scene_data)
            
            step_result.status = StepStatus.COMPLETED
            step_result.output_data = prompt_result
            
            # Save to database
            if db:
                step_db = self.save_pipeline_step(db, step_result, json.dumps(scene_data))
                
                # Save input and output
                self.save_pipeline_file(db, step_db.id, "scene_data.json", "input", 
                                      file_text=json.dumps(scene_data, indent=2))
                self.save_pipeline_file(db, step_db.id, "prompts.json", "output", 
                                      file_text=json.dumps(prompt_result, indent=2))
            
        except Exception as e:
            print(f"Error in prompt generation step: {e}")
            import traceback
            traceback.print_exc()
            
            step_result.status = StepStatus.FAILED
            step_result.error_message = str(e)
            step_result.output_data = None
            
            if db:
                self.save_pipeline_step(db, step_result, json.dumps(scene_data) if scene_data else None)
        
        step_result.processing_time = time.time() - step_start
        self.steps_results.append(step_result)
        return step_result
    
    async def _run_image_step(self, prompt_data: Any, db: Session = None) -> StepResult:
        """Run image generation step"""
        step_start = time.time()
        step_result = StepResult(step_name="Image Generation", status=StepStatus.RUNNING, processing_time=0)

        try:
            # Select image maker
            image_maker = ImageMakerSelector.get_image_maker(self.config.image_maker_type)
            image_manager = ImageMakerManager(image_maker)

            # Generate images (PIL.Image objects)
            generated_images = image_manager.process(prompt_data)

            # Save images to disk and collect file paths
            output_dir = self.output_dir or "outputs"
            os.makedirs(output_dir, exist_ok=True)
            image_paths = []

            for i, img in enumerate(generated_images):
                if img is None:
                    continue  # Skip failed images
                file_path = os.path.join(output_dir, f"generated_image_{i+1}.png")
                img.save(file_path)
                image_paths.append(file_path)

            # Step result
            step_result.status = StepStatus.COMPLETED
            step_result.output_data = image_paths
            step_result.output_files = image_paths

            # Save to DB
            if db:
                step_db = self.save_pipeline_step(db, step_result, json.dumps(prompt_data))

                # Save input JSON
                self.save_pipeline_file(
                    db, step_db.id, "image_input.json", "input",
                    file_text=json.dumps(prompt_data, indent=2)
                )

                # Save output images to DB as binary
                for i, file_path in enumerate(image_paths):
                    with open(file_path, 'rb') as f:
                        image_bytes = f.read()
                    image_filename = os.path.basename(file_path)
                    self.save_pipeline_file(db, step_db.id, image_filename, "image", file_content=image_bytes)

        except Exception as e:
            step_result.status = StepStatus.FAILED
            step_result.error_message = str(e)
            step_result.output_data = []

            if db:
                self.save_pipeline_step(
                    db,
                    step_result,
                    json.dumps(prompt_data) if prompt_data else None
                )

        step_result.processing_time = time.time() - step_start
        self.steps_results.append(step_result)
        return step_result
    
    def _determine_pipeline_status(self) -> PipelineStatus:
        """Determine overall pipeline status based on step results"""
        failed_steps = [step for step in self.steps_results if step.status == StepStatus.FAILED]
        completed_steps = [step for step in self.steps_results if step.status == StepStatus.COMPLETED]
        
        if len(failed_steps) == 0:
            return PipelineStatus.COMPLETED
        elif len(completed_steps) > 0:
            return PipelineStatus.PARTIAL_SUCCESS
        else:
            return PipelineStatus.FAILED
    
    def _create_failed_result(self, start_time: datetime, error_message: str, 
                            db: Session = None) -> PipelineResult:
        """Create a failed pipeline result"""
        end_time = datetime.utcnow()
        total_time = (end_time - start_time).total_seconds()
        
        # Update pipeline execution in database
        if db:
            self.save_pipeline_execution(db, PipelineStatus.FAILED, start_time, 
                                       end_time, total_time, error_message)
            db.commit()
        
        return PipelineResult(
            pipeline_id=self.pipeline_id or "unknown",
            status=PipelineStatus.FAILED,
            total_processing_time=total_time,
            output_directory=self.output_dir or "",
            steps=self.steps_results,
            final_images=[],
            metadata={"error": error_message}
        )
    
    def get_pipeline_status(self, pipeline_id: str) -> Optional[PipelineResult]:
        """Get pipeline execution status from database"""
        if not self.db_engine:
            return None
        
        db = self.db_engine.get_session()
        try:
            crud = PipelineCRUD(db)
            
            # Get pipeline execution
            pipeline_execution = crud.get_pipeline_execution(pipeline_id)
            if not pipeline_execution:
                return None
            
            # Get pipeline steps
            steps = crud.get_pipeline_steps(pipeline_id)
            
            # Convert to StepResult objects
            step_results = []
            for step in steps:
                step_result = StepResult(
                    step_name=step.step_name,
                    status=StepStatus(step.status),
                    processing_time=step.processing_time or 0,
                    output_data=json.loads(step.output_data) if step.output_data else None,
                    error_message=step.error_message
                )
                step_results.append(step_result)
            
            # Get final images
            final_images = []
            image_files = crud.get_pipeline_files(pipeline_id, file_type="image")
            for image_file in image_files:
                final_images.append(image_file.file_name)
            
            return PipelineResult(
                pipeline_id=pipeline_execution.pipeline_id,
                status=PipelineStatus(pipeline_execution.status),
                total_processing_time=pipeline_execution.total_processing_time or 0,
                output_directory="",  # Not used in DB version
                steps=step_results,
                final_images=final_images,
                metadata=json.loads(pipeline_execution.config) if pipeline_execution.config else {}
            )
            
        except Exception as e:
            print(f"Error getting pipeline status: {e}")
            return None
        finally:
            db.close()