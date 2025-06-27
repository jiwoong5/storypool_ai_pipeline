#response
import base64

import uvicorn

#ocr
from ocr.ocr_selector import OCRSelector
from api_responses.responses import OCRResponse
from api_requests.requests import OCRRequest

#translator
from translator.translator_selector import TranslatorSelector
from translator.translator_manager import TranslatorManager

#story_writer
from story_writer.story_writer_selector import StoryWriterSelector
from story_writer.story_writer_manager import StoryWriterManager

#Scene Parser
from scene_parser.scene_parser_selector import SceneParserSelector
from scene_parser.scene_parser_manager import SceneParserManager

#Prompt Maker
from prompt_maker.prompt_maker_selector import PromptMakerSelector
from prompt_maker.prompt_maker_manager import PromptMakerManager

#Emotion Classifier
from emotion_classifier.emotion_classifier_selector import EmotionClassifierSelector
from emotion_classifier.emotion_classifier_manager import EmotionClassifierManager

#Image Maker
from image_maker.image_maker_selector import ImageMakerSelector
from image_maker.image_maker_manager import ImageMakerManager

from constants.results_storage_paths.paths import *
from constants.page_paths.paths import *
from fastapi import FastAPI, HTTPException

app=FastAPI()

#ocr api
@app.post(OCR_ROUTE, response_model=OCRResponse)
async def process_ocr(request: OCRRequest):
    try:
        # Decode base64 image data
        image_data = base64.b64decode(request.image_data)

        ocr_manager = OCRSelector.get_reader("easyocr")
        # Process the image using OCRManager
        text_list = ocr_manager.read_text(image_data)

        if text_list is None:
            return OCRResponse(status="error", error_message="OCR processing failed")

        return OCRResponse(status="success", text_list=text_list)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing image: {str(e)}")

if __name__ == "__main__":
    # Run the API server
    uvicorn.run(app, host="0.0.0.0", port=8000)