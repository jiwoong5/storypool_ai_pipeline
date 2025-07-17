import os
import json
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
from fastapi import UploadFile
from constants.configs.configs import PipelineConfig
from pipeline.pipeline_models import *

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
from emotion_classifier.emotion_classifier_selector import EmotionClassifierSelector
from emotion_classifier.emotion_classifier_manager import EmotionClassifierManager
from image_maker.image_maker_selector import ImageMakerSelector
from image_maker.image_maker_manager import ImageMakerManager
        
# Main Pipeline Class
class AIProcessingPipeline:
    def __init__(self, config: PipelineConfig = None):
        self.config = config or PipelineConfig()
        self.pipeline_id = None
        self.output_dir = None
        self.steps_results = []
        
    def generate_pipeline_id(self) -> str:
        """Generate unique pipeline ID"""
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        return f"pipeline_{timestamp}_{os.urandom(4).hex()}"
    
    async def run_from_file(self, file: UploadFile) -> PipelineResult:
        from apis import create_output_directory
        """Run complete pipeline from uploaded file"""
        start_time = time.time()
        self.pipeline_id = self.generate_pipeline_id()
        self.output_dir = create_output_directory(f"pipeline_{self.pipeline_id}")
        
        try:
            # Step 1: OCR - Extract text from image
            ocr_result = await self._run_ocr_step(file)
            if ocr_result.status == StepStatus.FAILED and not self.config.continue_on_error:
                return self._create_failed_result(start_time, "OCR step failed")
            
            # Step 2: Translation - Translate extracted text
            translation_result = await self._run_translation_step(ocr_result.output_data)
            if translation_result.status == StepStatus.FAILED and not self.config.continue_on_error:
                return self._create_failed_result(start_time, "Translation step failed")
            
            # Step 3: Story Generation - Create story from translated text
            story_result = await self._run_story_step(translation_result.output_data)
            if story_result.status == StepStatus.FAILED and not self.config.continue_on_error:
                return self._create_failed_result(start_time, "Story generation step failed")
            
            # Step 4: Scene Parsing - Parse scenes from story
            scene_result = await self._run_scene_step(story_result.output_data)
            if scene_result.status == StepStatus.FAILED and not self.config.continue_on_error:
                return self._create_failed_result(start_time, "Scene parsing step failed")
            
            # Step 5: Prompt Generation - Generate prompts from scenes
            prompt_result = await self._run_prompt_step(scene_result.output_data)
            if prompt_result.status == StepStatus.FAILED and not self.config.continue_on_error:
                return self._create_failed_result(start_time, "Prompt generation step failed")
            
            # Step 6: Image Generation - Generate images from prompts
            image_result = await self._run_image_step(prompt_result.output_data)
            
            # Create final result
            total_time = time.time() - start_time
            pipeline_status = self._determine_pipeline_status()
            
            return PipelineResult(
                pipeline_id=self.pipeline_id,
                status=pipeline_status,
                total_processing_time=total_time,
                output_directory=self.output_dir,
                steps=self.steps_results,
                final_images=image_result.output_files if image_result.output_files else [],
                metadata={"config": self.config.__dict__}
            )
            
        except Exception as e:
            return self._create_failed_result(start_time, f"Pipeline execution failed: {str(e)}")
    
    async def run_from_text(self, text: str) -> PipelineResult:
        from apis import create_output_directory, save_uploaded_file
        """Run pipeline starting from text (skip OCR step)"""
        start_time = time.time()
        self.pipeline_id = self.generate_pipeline_id()
        self.output_dir = create_output_directory(f"pipeline_{self.pipeline_id}")
        
        try:
            # Skip OCR, start from translation
            translation_result = await self._run_translation_step(text)
            if translation_result.status == StepStatus.FAILED and not self.config.continue_on_error:
                return self._create_failed_result(start_time, "Translation step failed")
            
            # Continue with remaining steps...
            story_result = await self._run_story_step(translation_result.output_data)
            scene_result = await self._run_scene_step(story_result.output_data)
            prompt_result = await self._run_prompt_step(scene_result.output_data)
            image_result = await self._run_image_step(prompt_result.output_data)
            
            total_time = time.time() - start_time
            pipeline_status = self._determine_pipeline_status()
            
            return PipelineResult(
                pipeline_id=self.pipeline_id,
                status=pipeline_status,
                total_processing_time=total_time,
                output_directory=self.output_dir,
                steps=self.steps_results,
                final_images=image_result.output_files if image_result.output_files else [],
                metadata={"config": self.config.__dict__}
            )
            
        except Exception as e:
            return self._create_failed_result(start_time, f"Pipeline execution failed: {str(e)}")
    
    async def _run_ocr_step(self, file: UploadFile) -> StepResult:
        from apis import save_uploaded_file
        """Run OCR step"""
        step_start = time.time()
        step_result = StepResult(step_name="OCR", status=StepStatus.RUNNING, processing_time=0)
        
        try:
            # Save uploaded file
            file_path = await save_uploaded_file(file, self.output_dir)
            
            # Run OCR
            ocr_model = OCRSelector.get_reader(self.config.ocr_reader_type)
            ocr_manager = OCRManager(ocr_model)
            
            ocr_output_path = os.path.join(self.output_dir, "01_ocr_result.txt")
            ocr_manager.process_from_path(file_path, ocr_output_path)
            
            # Read extracted text
            extracted_text = ""
            if os.path.exists(ocr_output_path):
                with open(ocr_output_path, 'r', encoding='utf-8') as f:
                    extracted_text = f.read()
            
            step_result.status = StepStatus.COMPLETED
            step_result.output_data = extracted_text
            step_result.output_files = [ocr_output_path]
            
        except Exception as e:
            step_result.status = StepStatus.FAILED
            step_result.error_message = str(e)
        
        step_result.processing_time = time.time() - step_start
        self.steps_results.append(step_result)
        return step_result
    
    async def _run_translation_step(self, input_text: str) -> StepResult:
        """Run translation step"""
        step_start = time.time()
        step_result = StepResult(step_name="Translation", status=StepStatus.RUNNING, processing_time=0)
        
        try:
            # Save input text
            input_path = os.path.join(self.output_dir, "02_translation_input.txt")
            with open(input_path, 'w', encoding='utf-8') as f:
                f.write(input_text)
            
            # Run translation
            translator = TranslatorSelector.get_translator(self.config.translator_type)
            translator_manager = TranslatorManager(translator)
            
            output_path = os.path.join(self.output_dir, "02_translated.txt")
            translator_manager.process(input_path, output_path)
            
            # Read translated text
            translated_text = ""
            if os.path.exists(output_path):
                with open(output_path, 'r', encoding='utf-8') as f:
                    translated_text = f.read()
            
            step_result.status = StepStatus.COMPLETED
            step_result.output_data = translated_text
            step_result.output_files = [output_path]
            
        except Exception as e:
            step_result.status = StepStatus.FAILED
            step_result.error_message = str(e)
            # Use original text if translation fails
            step_result.output_data = input_text
        
        step_result.processing_time = time.time() - step_start
        self.steps_results.append(step_result)
        return step_result
    
    async def _run_story_step(self, input_text: str) -> StepResult:
        """Run story generation step"""
        step_start = time.time()
        step_result = StepResult(step_name="Story Generation", status=StepStatus.RUNNING, processing_time=0)
        
        try:
            # Save input text
            input_path = os.path.join(self.output_dir, "03_story_input.txt")
            with open(input_path, 'w', encoding='utf-8') as f:
                f.write(input_text)
            
            # Generate story
            story_writer = StoryWriterSelector.get_writer(self.config.story_writer_type)
            story_manager = StoryWriterManager(story_writer)
            
            output_path = os.path.join(self.output_dir, "03_story.txt")
            story_manager.process(input_path, output_path)
            
            # Read generated story
            generated_story = ""
            if os.path.exists(output_path):
                with open(output_path, 'r', encoding='utf-8') as f:
                    generated_story = f.read()
            
            step_result.status = StepStatus.COMPLETED
            step_result.output_data = generated_story
            step_result.output_files = [output_path]
            
        except Exception as e:
            step_result.status = StepStatus.FAILED
            step_result.error_message = str(e)
            step_result.output_data = input_text  # Fallback to input
        
        step_result.processing_time = time.time() - step_start
        self.steps_results.append(step_result)
        return step_result
    
    async def _run_scene_step(self, story_text: str) -> StepResult:
        """Run scene parsing step"""
        step_start = time.time()
        step_result = StepResult(step_name="Scene Parsing", status=StepStatus.RUNNING, processing_time=0)
        
        try:
            # Save story text
            input_path = os.path.join(self.output_dir, "04_scene_input.txt")
            with open(input_path, 'w', encoding='utf-8') as f:
                f.write(story_text)
            
            # Parse scenes
            scene_parser = SceneParserSelector.get_parser(self.config.scene_parser_type)
            scene_parser_manager = SceneParserManager(scene_parser)
            
            output_path = os.path.join(self.output_dir, "04_scenes.json")
            scene_response = scene_parser_manager.process(input_path, output_path)
            
            step_result.status = StepStatus.COMPLETED
            step_result.output_data = scene_response
            step_result.output_files = [output_path]
            
        except Exception as e:
            step_result.status = StepStatus.FAILED
            step_result.error_message = str(e)
            step_result.output_data = None
        
        step_result.processing_time = time.time() - step_start
        self.steps_results.append(step_result)
        return step_result
    
    async def _run_prompt_step(self, scene_data: Any) -> StepResult:
        """Run prompt generation step"""
        step_start = time.time()
        step_result = StepResult(step_name="Prompt Generation", status=StepStatus.RUNNING, processing_time=0)
        
        try:
            # 04_scenes.json 파일 경로 (scene parsing 단계에서 생성된 파일)
            input_path = os.path.join(self.output_dir, "04_scenes.json")
            output_path = os.path.join(self.output_dir, "05_prompts.json")
            
            # 프롬프트 생성 처리
            prompt_maker = PromptMakerSelector.get_prompt_maker(self.config.prompt_maker_type)
            prompt_manager = PromptMakerManager(prompt_maker)
            
            prompt_result = prompt_manager.process(input_path, output_path)
            
            step_result.status = StepStatus.COMPLETED
            step_result.output_data = prompt_result
            step_result.output_files = [output_path]
            
        except Exception as e:
            print(f"Error in prompt generation step: {e}")
            import traceback
            traceback.print_exc()
            
            step_result.status = StepStatus.FAILED
            step_result.error_message = str(e)
            step_result.output_data = None
        
        step_result.processing_time = time.time() - step_start
        self.steps_results.append(step_result)
        return step_result
    
    async def _run_image_step(self, prompt_data: Any) -> StepResult:
        """Run image generation step"""
        step_start = time.time()
        step_result = StepResult(step_name="Image Generation", status=StepStatus.RUNNING, processing_time=0)
        
        try:
            # Save prompt data
            input_path = os.path.join(self.output_dir, "06_image_input.json")
            with open(input_path, 'w', encoding='utf-8') as f:
                if prompt_data:
                    json.dump(prompt_data, f, indent=2)
                else:
                    f.write("No prompt data available")
            
            # Generate images
            image_maker = ImageMakerSelector.get_image_maker(self.config.image_maker_type)
            image_manager = ImageMakerManager(image_maker)
            
            image_output_dir = os.path.join(self.output_dir, "06_generated_images")
            os.makedirs(image_output_dir, exist_ok=True)
            
            image_manager.process(input_path, image_output_dir)
            
            # List generated images
            generated_images = []
            if os.path.exists(image_output_dir):
                for file in os.listdir(image_output_dir):
                    if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                        generated_images.append(os.path.join(image_output_dir, file))
            
            step_result.status = StepStatus.COMPLETED
            step_result.output_data = generated_images
            step_result.output_files = generated_images
            
        except Exception as e:
            step_result.status = StepStatus.FAILED
            step_result.error_message = str(e)
            step_result.output_data = []
        
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
    
    def _create_failed_result(self, start_time: float, error_message: str) -> PipelineResult:
        """Create a failed pipeline result"""
        return PipelineResult(
            pipeline_id=self.pipeline_id or "unknown",
            status=PipelineStatus.FAILED,
            total_processing_time=time.time() - start_time,
            output_directory=self.output_dir or "",
            steps=self.steps_results,
            final_images=[],
            metadata={"error": error_message}
        )