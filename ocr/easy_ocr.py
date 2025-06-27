from ocr.ocr_interface import OCRInterface
import easyocr
from PIL import Image
import io
import numpy as np


class EasyOCR(OCRInterface):
    def __init__(self):
        self.reader = easyocr.Reader(['ko', 'en'])  # 기본 한글, 영어

    def read_text(self, image_data: bytes, lang_list: list = ['ko', 'en']) -> list:
        image = Image.open(io.BytesIO(image_data))

        image_np = np.array(image)

        self.reader = easyocr.Reader(lang_list)

        results = self.reader.readtext(image_np, detail=0)  # 텍스트만 추출
        return results
