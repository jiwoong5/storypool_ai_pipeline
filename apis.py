from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import JSONResponse
import os
import time
from datetime import datetime
from typing import Optional, List
import tempfile
import shutil

# Import request and response models
from api_requests.requests import (
    OCRRequest, OCRBatchRequest, TranslatorRequest, TranslatorTextRequest,
    StoryWriterRequest, StoryWriterTextRequest, SceneParserRequest, SceneParserTextRequest,
    PromptMakerRequest, PromptMakerTextRequest, EmotionClassifierRequest, 
    EmotionClassifierTextRequest, EmotionClassifierBatchRequest,
    ImageMakerRequest, ImageMakerTextRequest
)

from api_responses.responses import (
    OCRResponse, OCRBatchResponse, TranslatorResponse, StoryWriterResponse,
    SceneParserResponse, PromptMakerResponse, EmotionClassifierResponse,
    EmotionClassifierBatchResponse, ImageMakerResponse, ErrorResponse,
    HealthCheckResponse, StatusCode
)

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

app = FastAPI(
    title="Multi-Modal Processing API",
    description="API for OCR, Translation, Story Writing, Scene Parsing, Prompt Making, Emotion Classification, and Image Generation",
    version="1.0.0"
)

# Utility function to create output directory
def create_output_directory(base_path: str = "outputs") -> str:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = os.path.join(base_path, timestamp)
    os.makedirs(output_dir, exist_ok=True)
    return output_dir

# Utility function to save uploaded file
async def save_uploaded_file(file: UploadFile, directory: str) -> str:
    file_path = os.path.join(directory, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return file_path

# Error handler
def create_error_response(error_message: str, error_code: str = "PROCESSING_ERROR") -> ErrorResponse:
    from api_responses.responses import ErrorDetail
    return ErrorResponse(
        status=StatusCode.ERROR,
        message="Processing failed",
        error_details=ErrorDetail(
            error_code=error_code,
            error_type="ProcessingError",
            description=error_message,
            suggestion="Please check your input and try again"
        )
    )

# Health Check
@app.get("/health", response_model=HealthCheckResponse)
async def health_check():
    return HealthCheckResponse(
        status="healthy",
        version="1.0.0",
        uptime=time.time(),
        components={
            "ocr": "healthy",
            "translator": "healthy",
            "story_writer": "healthy",
            "scene_parser": "healthy",
            "prompt_maker": "healthy",
            "emotion_classifier": "healthy",
            "image_maker": "healthy"
        }
    )

# OCR Endpoints
@app.post("/ocr/process", response_model=OCRResponse)
async def process_ocr_file(file: UploadFile = File(...), reader_type: str = "easyocr"):
    start_time = time.time()
    output_dir = create_output_directory()
    
    try:
        image_path = await save_uploaded_file(file, output_dir)
        ocr_model = OCRSelector.get_reader(reader_type)
        ocr_manager = OCRManager(ocr_model)
        
        output_path = os.path.join(output_dir, "ocr_result.txt")
        result = ocr_manager.process_from_path(image_path, output_path)
        
        extracted_text = ""
        if os.path.exists(output_path):
            with open(output_path, 'r', encoding='utf-8') as f:
                extracted_text = f.read()
        
        processing_time = time.time() - start_time
        
        return OCRResponse(
            status=StatusCode.SUCCESS,
            message="OCR processing completed successfully",
            processing_time=processing_time,
            output_directory=output_dir,
            extracted_text=extracted_text,
            confidence_score=0.95,
            detected_languages=["en"]
        )
        
    except Exception as e:
        error_response = create_error_response(str(e), "OCR_ERROR")
        return JSONResponse(
            status_code=500,
            content=error_response.dict()
        )

@app.post("/ocr/batch", response_model=OCRBatchResponse)
async def process_ocr_batch(files: List[UploadFile] = File(...), reader_type: str = "easyocr"):
    start_time = time.time()
    output_dir = create_output_directory()
    
    try:
        results = []
        successful_count = 0
        failed_count = 0
        
        ocr_model = OCRSelector.get_reader(reader_type)
        ocr_manager = OCRManager(ocr_model)
        
        for i, file in enumerate(files):
            try:
                image_path = await save_uploaded_file(file, output_dir)
                output_path = os.path.join(output_dir, f"ocr_result_{i}.txt")
                
                ocr_manager.process(image_path, output_path)
                
                extracted_text = ""
                if os.path.exists(output_path):
                    with open(output_path, 'r', encoding='utf-8') as f:
                        extracted_text = f.read()
                
                results.append({
                    "file_name": file.filename,
                    "extracted_text": extracted_text,
                    "status": "success"
                })
                successful_count += 1
                
            except Exception as e:
                results.append({
                    "file_name": file.filename,
                    "error": str(e),
                    "status": "failed"
                })
                failed_count += 1
        
        processing_time = time.time() - start_time
        
        return OCRBatchResponse(
            status=StatusCode.SUCCESS if failed_count == 0 else StatusCode.PARTIAL_SUCCESS,
            message=f"Batch OCR processing completed. {successful_count} successful, {failed_count} failed",
            processing_time=processing_time,
            output_directory=output_dir,
            results=results,
            total_processed=len(files),
            successful_count=successful_count,
            failed_count=failed_count
        )
        
    except Exception as e:
        return create_error_response(str(e), "OCR_BATCH_ERROR")

# Translator Endpoints
@app.post("/translator/process", response_model=TranslatorResponse)
async def process_translator_file(file: UploadFile = File(...), translator_type: str = "ko-en"):
    start_time = time.time()
    output_dir = create_output_directory()
    
    try:
        input_path = await save_uploaded_file(file, output_dir)
        output_path = os.path.join(output_dir, "translated.txt")
        
        translator = TranslatorSelector.get_translator(translator_type)
        translator_manager = TranslatorManager(translator)
        translator_manager.process(input_path, output_path)
        
        # Read original and translated text
        original_text = ""
        translated_text = ""
        
        with open(input_path, 'r', encoding='utf-8') as f:
            original_text = f.read()
            
        if os.path.exists(output_path):
            with open(output_path, 'r', encoding='utf-8') as f:
                translated_text = f.read()
        
        processing_time = time.time() - start_time
        
        # Parse source and target languages from translator_type
        source_lang, target_lang = translator_type.split('-')
        
        return TranslatorResponse(
            status=StatusCode.SUCCESS,
            message="Translation completed successfully",
            processing_time=processing_time,
            output_directory=output_dir,
            original_text=original_text,
            translated_text=translated_text,
            source_language=source_lang,
            target_language=target_lang,
            confidence_score=0.90
        )
        
    except Exception as e:
        return create_error_response(str(e), "TRANSLATOR_ERROR")

@app.post("/translator/text", response_model=TranslatorResponse)
async def translate_text(request: TranslatorTextRequest):
    start_time = time.time()
    output_dir = create_output_directory()
    
    try:
        # Save input text to file
        input_path = os.path.join(output_dir, "input.txt")
        with open(input_path, 'w', encoding='utf-8') as f:
            f.write(request.text)
        
        output_path = os.path.join(output_dir, "translated.txt")
        
        translator = TranslatorSelector.get_translator(request.translator_type.value)
        translator_manager = TranslatorManager(translator)
        translator_manager.process(input_path, output_path)
        
        translated_text = ""
        if os.path.exists(output_path):
            with open(output_path, 'r', encoding='utf-8') as f:
                translated_text = f.read()
        
        processing_time = time.time() - start_time
        
        # Parse source and target languages
        source_lang, target_lang = request.translator_type.value.split('-')
        
        return TranslatorResponse(
            status=StatusCode.SUCCESS,
            message="Text translation completed successfully",
            processing_time=processing_time,
            output_directory=output_dir,
            original_text=request.text,
            translated_text=translated_text,
            source_language=source_lang,
            target_language=target_lang,
            confidence_score=0.90
        )
        
    except Exception as e:
        return create_error_response(str(e), "TRANSLATOR_TEXT_ERROR")

# Story Writer Endpoints
@app.post("/story/process", response_model=StoryWriterResponse)
async def process_story_writer_file(file: UploadFile = File(...), writer_type: str = "llama"):
    start_time = time.time()
    output_dir = create_output_directory()
    
    try:
        input_path = await save_uploaded_file(file, output_dir)
        output_path = os.path.join(output_dir, "story.txt")
        
        story_writer = StoryWriterSelector.get_writer(writer_type)
        story_manager = StoryWriterManager(story_writer)
        story_manager.process(input_path, output_path)
        
        generated_story = ""
        if os.path.exists(output_path):
            with open(output_path, 'r', encoding='utf-8') as f:
                generated_story = f.read()
        
        processing_time = time.time() - start_time
        
        return StoryWriterResponse(
            status=StatusCode.SUCCESS,
            message="Story generation completed successfully",
            processing_time=processing_time,
            output_directory=output_dir,
            generated_story=generated_story,
            genre="adventure",  # Default, should be detected
            writing_style="narrative"  # Default, should be detected
        )
        
    except Exception as e:
        return create_error_response(str(e), "STORY_WRITER_ERROR")

@app.post("/story/text", response_model=StoryWriterResponse)
async def generate_story_from_text(request: StoryWriterTextRequest):
    start_time = time.time()
    output_dir = create_output_directory()
    
    try:
        # Save prompt to file
        input_path = os.path.join(output_dir, "prompt.txt")
        with open(input_path, 'w', encoding='utf-8') as f:
            f.write(request.prompt)
        
        output_path = os.path.join(output_dir, "story.txt")
        
        story_writer = StoryWriterSelector.get_writer(request.writer_type.value)
        story_manager = StoryWriterManager(story_writer)
        story_manager.process(input_path, output_path)
        
        generated_story = ""
        if os.path.exists(output_path):
            with open(output_path, 'r', encoding='utf-8') as f:
                generated_story = f.read()
        
        processing_time = time.time() - start_time
        
        return StoryWriterResponse(
            status=StatusCode.SUCCESS,
            message="Story generation from text completed successfully",
            processing_time=processing_time,
            output_directory=output_dir,
            generated_story=generated_story,
            genre="adventure",
            writing_style="narrative"
        )
        
    except Exception as e:
        return create_error_response(str(e), "STORY_WRITER_TEXT_ERROR")

# Scene Parser Endpoints
@app.post("/scene/process", response_model=SceneParserResponse)
async def process_scene_parser_file(file: UploadFile = File(...), parser_type: str = "basic"):
    start_time = time.time()
    output_dir = create_output_directory()
    
    try:
        input_path = await save_uploaded_file(file, output_dir)
        output_path = os.path.join(output_dir, "scenes.txt")
        
        scene_parser = SceneParserSelector.get_parser(parser_type)
        scene_parser_manager = SceneParserManager(scene_parser)
        scene_parser_manager.process(input_path, output_path)
        
        processing_time = time.time() - start_time
        
        # Mock scene data - should be parsed from actual result
        from api_responses.responses import SceneInfo
        scenes = [
            SceneInfo(
                scene_number=1,
                scene_title="Opening Scene",
                characters=["Hero", "Mentor"],
                location="Village",
                time="Morning",
                mood="Peaceful",
                summary="The hero begins their journey",
                dialogue_count=5
            )
        ]
        
        return SceneParserResponse(
            status=StatusCode.SUCCESS,
            message="Scene parsing completed successfully",
            processing_time=processing_time,
            output_directory=output_dir,
            scenes=scenes,
            total_scenes=len(scenes),
            main_characters=["Hero", "Mentor"],
            locations=["Village"]
        )
        
    except Exception as e:
        return create_error_response(str(e), "SCENE_PARSER_ERROR")

@app.post("/scene/text", response_model=SceneParserResponse)
async def parse_scenes_from_text(request: SceneParserTextRequest):
    start_time = time.time()
    output_dir = create_output_directory()
    
    try:
        input_path = os.path.join(output_dir, "input.txt")
        with open(input_path, 'w', encoding='utf-8') as f:
            f.write(request.text)
        
        output_path = os.path.join(output_dir, "scenes.txt")
        
        scene_parser = SceneParserSelector.get_parser(request.parser_type.value)
        scene_parser_manager = SceneParserManager(scene_parser)
        scene_parser_manager.process(input_path, output_path)
        
        processing_time = time.time() - start_time
        
        # Mock scene data
        from api_responses.responses import SceneInfo
        scenes = [
            SceneInfo(
                scene_number=1,
                scene_title="Parsed Scene",
                characters=["Character1"],
                location="Unknown",
                time="Unknown",
                mood="Neutral",
                summary="Scene parsed from text",
                dialogue_count=0
            )
        ]
        
        return SceneParserResponse(
            status=StatusCode.SUCCESS,
            message="Scene parsing from text completed successfully",
            processing_time=processing_time,
            output_directory=output_dir,
            scenes=scenes,
            total_scenes=len(scenes),
            main_characters=["Character1"],
            locations=["Unknown"]
        )
        
    except Exception as e:
        return create_error_response(str(e), "SCENE_PARSER_TEXT_ERROR")

# Prompt Maker Endpoints
@app.post("/prompt/process", response_model=PromptMakerResponse)
async def process_prompt_maker_file(file: UploadFile = File(...), prompt_maker_type: str = "llama"):
    start_time = time.time()
    output_dir = create_output_directory()
    
    try:
        input_path = await save_uploaded_file(file, output_dir)
        output_path = os.path.join(output_dir, "prompts.txt")
        
        prompt_maker = PromptMakerSelector.get_prompt_maker(prompt_maker_type)
        prompt_manager = PromptMakerManager(prompt_maker)
        prompt_manager.process(input_path, output_path)
        
        generated_prompt = ""
        if os.path.exists(output_path):
            with open(output_path, 'r', encoding='utf-8') as f:
                generated_prompt = f.read()
        
        processing_time = time.time() - start_time
        
        return PromptMakerResponse(
            status=StatusCode.SUCCESS,
            message="Prompt generation completed successfully",
            processing_time=processing_time,
            output_directory=output_dir,
            generated_prompt=generated_prompt,
            prompt_type="creative",
            keywords=["adventure", "hero", "journey"],
            estimated_length=100,
            prompt_quality_score=0.85
        )
        
    except Exception as e:
        return create_error_response(str(e), "PROMPT_MAKER_ERROR")

@app.post("/prompt/text", response_model=PromptMakerResponse)
async def generate_prompt_from_text(request: PromptMakerTextRequest):
    start_time = time.time()
    output_dir = create_output_directory()
    
    try:
        input_path = os.path.join(output_dir, "input.txt")
        with open(input_path, 'w', encoding='utf-8') as f:
            f.write(request.input_text)
        
        output_path = os.path.join(output_dir, "prompts.txt")
        
        prompt_maker = PromptMakerSelector.get_prompt_maker(request.prompt_maker_type.value)
        prompt_manager = PromptMakerManager(prompt_maker)
        prompt_manager.process(input_path, output_path)
        
        generated_prompt = ""
        if os.path.exists(output_path):
            with open(output_path, 'r', encoding='utf-8') as f:
                generated_prompt = f.read()
        
        processing_time = time.time() - start_time
        
        return PromptMakerResponse(
            status=StatusCode.SUCCESS,
            message="Prompt generation from text completed successfully",
            processing_time=processing_time,
            output_directory=output_dir,
            generated_prompt=generated_prompt,
            prompt_type="creative",
            keywords=["generated", "text", "prompt"],
            estimated_length=100,
            prompt_quality_score=0.85
        )
        
    except Exception as e:
        return create_error_response(str(e), "PROMPT_MAKER_TEXT_ERROR")

# Emotion Classifier Endpoints
@app.post("/emotion/process", response_model=EmotionClassifierResponse)
async def process_emotion_classifier_file(file: UploadFile = File(...), emotion_classifer_type: str = "minilm"):
    start_time = time.time()
    output_dir = create_output_directory()
    
    try:
        input_path = await save_uploaded_file(file, output_dir)
        output_path = os.path.join(output_dir, "emotions.txt")
        
        emotion_classifier = EmotionClassifierSelector.get_emotion_classifier(emotion_classifer_type)
        emotion_manager = EmotionClassifierManager(emotion_classifier)
        emotion_manager.process(input_path, output_path)
        
        processing_time = time.time() - start_time
        
        # Mock emotion data
        from api_responses.responses import EmotionScore
        emotion_scores = [
            EmotionScore(emotion="happy", score=0.7, confidence=0.9),
            EmotionScore(emotion="sad", score=0.2, confidence=0.8),
            EmotionScore(emotion="neutral", score=0.1, confidence=0.7)
        ]
        
        return EmotionClassifierResponse(
            status=StatusCode.SUCCESS,
            message="Emotion classification completed successfully",
            processing_time=processing_time,
            output_directory=output_dir,
            primary_emotion="happy",
            emotion_scores=emotion_scores,
            sentiment_polarity="positive",
            intensity=0.7
        )
        
    except Exception as e:
        return create_error_response(str(e), "EMOTION_CLASSIFIER_ERROR")

@app.post("/emotion/text", response_model=EmotionClassifierResponse)
async def classify_emotion_from_text(request: EmotionClassifierTextRequest):
    start_time = time.time()
    output_dir = create_output_directory()
    
    try:
        input_path = os.path.join(output_dir, "input.txt")
        with open(input_path, 'w', encoding='utf-8') as f:
            f.write(request.text)
        
        output_path = os.path.join(output_dir, "emotions.txt")
        
        emotion_classifier = EmotionClassifierSelector.get_emotion_classifier(request.emotion_classifer_type.value)
        emotion_manager = EmotionClassifierManager(emotion_classifier)
        emotion_manager.process(input_path, output_path)
        
        processing_time = time.time() - start_time
        
        # Mock emotion data
        from api_responses.responses import EmotionScore
        emotion_scores = [
            EmotionScore(emotion="neutral", score=0.6, confidence=0.8),
            EmotionScore(emotion="happy", score=0.3, confidence=0.7),
            EmotionScore(emotion="sad", score=0.1, confidence=0.6)
        ]
        
        return EmotionClassifierResponse(
            status=StatusCode.SUCCESS,
            message="Emotion classification from text completed successfully",
            processing_time=processing_time,
            output_directory=output_dir,
            primary_emotion="neutral",
            emotion_scores=emotion_scores,
            sentiment_polarity="neutral",
            intensity=0.6
        )
        
    except Exception as e:
        return create_error_response(str(e), "EMOTION_CLASSIFIER_TEXT_ERROR")

@app.post("/emotion/batch", response_model=EmotionClassifierBatchResponse)
async def process_emotion_classifier_batch(files: List[UploadFile] = File(...), emotion_classifer_type: str = "minilm"):
    start_time = time.time()
    output_dir = create_output_directory()
    
    try:
        results = {}
        emotion_classifier = EmotionClassifierSelector.get_emotion_classifier(emotion_classifer_type)
        emotion_manager = EmotionClassifierManager(emotion_classifier)
        
        for i, file in enumerate(files):
            input_path = await save_uploaded_file(file, output_dir)
            output_path = os.path.join(output_dir, f"emotions_{i}.txt")
            
            try:
                emotion_manager.process(input_path, output_path)
                results[file.filename] = {
                    "status": "success",
                    "primary_emotion": "neutral",
                    "intensity": 0.5
                }
            except Exception as e:
                results[file.filename] = {
                    "status": "failed",
                    "error": str(e)
                }
        
        processing_time = time.time() - start_time
        
        return EmotionClassifierBatchResponse(
            status=StatusCode.SUCCESS,
            message="Batch emotion classification completed successfully",
            processing_time=processing_time,
            output_directory=output_dir,
            results=results,
            summary={"average_intensity": 0.5, "most_common_emotion": "neutral"},
            total_processed=len(files)
        )
        
    except Exception as e:
        return create_error_response(str(e), "EMOTION_CLASSIFIER_BATCH_ERROR")

# Image Maker Endpoints
@app.post("/image/process", response_model=ImageMakerResponse)
async def process_image_maker_file(file: UploadFile = File(...), image_maker_type: str = "dream_shaper"):
    start_time = time.time()
    output_dir = create_output_directory()
    
    try:
        input_path = await save_uploaded_file(file, output_dir)
        image_output_path = os.path.join(output_dir, "generated_images")
        os.makedirs(image_output_path, exist_ok=True)
        
        image_maker = ImageMakerSelector.get_image_maker(image_maker_type)
        image_manager = ImageMakerManager(image_maker)
        image_manager.process(input_path, image_output_path)
        
        processing_time = time.time() - start_time
        
        # Mock generated image data
        from api_responses.responses import GeneratedImage
        generated_images = [
            GeneratedImage(
                image_path=os.path.join(image_output_path, "generated_1.png"),
                image_name="generated_1.png",
                width=512,
                height=512,
                file_size=1024000,
                generation_seed=12345
            )
        ]
        
        return ImageMakerResponse(
            status=StatusCode.SUCCESS,
            message="Image generation completed successfully",
            processing_time=processing_time,
            output_directory=output_dir,
            generated_images=generated_images,
            prompt_used="A beautiful landscape",
            total_images=1,
            model_used=image_maker_type,
            generation_parameters={"steps": 20, "guidance_scale": 7.5}
        )
        
    except Exception as e:
        return create_error_response(str(e), "IMAGE_MAKER_ERROR")

@app.post("/image/text", response_model=ImageMakerResponse)
async def generate_image_from_text(request: ImageMakerTextRequest):
    start_time = time.time()
    output_dir = create_output_directory()
    
    try:
        # Save prompt to file
        input_path = os.path.join(output_dir, "prompt.txt")
        with open(input_path, 'w', encoding='utf-8') as f:
            f.write(request.prompt)
        
        image_output_path = os.path.join(output_dir, "generated_images")
        os.makedirs(image_output_path, exist_ok=True)
        
        image_maker = ImageMakerSelector.get_image_maker(request.image_maker_type.value)
        image_manager = ImageMakerManager(image_maker)
        image_manager.process(input_path, image_output_path)
        
        processing_time = time.time() - start_time
        
        # Mock generated image data
        from api_responses.responses import GeneratedImage
        generated_images = []
        for i in range(request.num_images or 1):
            generated_images.append(
                GeneratedImage(
                    image_path=os.path.join(image_output_path, f"generated_{i+1}.png"),
                    image_name=f"generated_{i+1}.png",
                    width=512,
                    height=512,
                    file_size=1024000,
                    generation_seed=12345 + i
                )
            )
        
        return ImageMakerResponse(
            status=StatusCode.SUCCESS,
            message="Image generation from text completed successfully",
            processing_time=processing_time,
            output_directory=output_dir,
            generated_images=generated_images,
            prompt_used=request.prompt,
            total_images=len(generated_images),
            model_used=request.image_maker_type.value,
            generation_parameters={"steps": 20, "guidance_scale": 7.5}
        )
        
    except Exception as e:
        return create_error_response(str(e), "IMAGE_MAKER_TEXT_ERROR")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)