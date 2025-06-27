from ocr.ocr_selector import OCRSelector
from ocr.ocr_manager import OCRManager
from constants.results_storage_paths.paths import *
from fastapi import FastAPI

app=FastAPI()
@app.get("/ocr")
def ocr():
    ocr_model = OCRSelector.get_reader("easyocr")
    ocr_manager = OCRManager(ocr_model)
    return ocr_manager.process(INPUT_IMAGE)
