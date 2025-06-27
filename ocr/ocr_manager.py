from ocr.ocr_interface import OCRInterface
from typing import List, Optional


class OCRManager:
    def __init__(self, ocr_engine: OCRInterface):
        self.ocr_engine = ocr_engine

    def process(self, image_data: bytes) -> Optional[List[str]]:
        print("[INFO] OCR 처리 시작")
        try:
            text_list = self.ocr_engine.read_text(image_data)
        except Exception as e:
            print(f"[ERROR] OCR 실패: {e}")
            return None

        print("[INFO] OCR 처리 완료")
        return text_list
