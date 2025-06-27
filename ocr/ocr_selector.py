from ocr.ocr_interface import OCRInterface
from ocr.easy_ocr import EasyOCR
class OCRSelector:
    @staticmethod
    def get_reader(engine: str = 'easyocr') -> OCRInterface:
        if engine == 'easyocr':
            return EasyOCR()
        # 다른 OCR 엔진 추가 가능 (예: TesseractReader)
        raise ValueError(f"Unsupported OCR engine: {engine}")