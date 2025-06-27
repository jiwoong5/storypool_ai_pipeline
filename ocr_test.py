from ocr.ocr_selector import OCRSelector
from ocr.ocr_manager import OCRManager

if __name__ == "__main__":
    ocr = OCRSelector.get_reader('easyocr')
    manager = OCRManager(ocr)
    print(manager.process("sample_image.png"))