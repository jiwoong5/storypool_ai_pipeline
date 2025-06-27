from ocr.ocr_interface import OCRInterface
from typing import List, Optional


class OCRManager:
    def __init__(self, ocr_engine: OCRInterface):
        self.ocr_engine = ocr_engine

    def process(self, image_data: bytes, output_path: Optional[str] = None) -> Optional[List[str]]:
        print("[INFO] OCR 처리 시작")
        try:
            # OCR 수행
            text_list = self.ocr_engine.read_text(image_data)

            # 파일로 저장
            if output_path and text_list:
                with open(output_path, 'w', encoding='utf-8') as f:
                    for line in text_list:
                        f.write(line + '\n')
                print(f"[INFO] OCR 결과가 파일에 저장되었습니다: {output_path}")

        except Exception as e:
            print(f"[ERROR] OCR 실패: {e}")
            return None

        print("[INFO] OCR 처리 완료")
        return text_list

    def process_from_path(self, input_path: str, output_path: Optional[str] = None) -> Optional[List[str]]:
        print(f"[INFO] 파일에서 이미지 읽기: {input_path}")
        try:
            with open(input_path, 'rb') as f:
                image_data = f.read()
        except Exception as e:
            print(f"[ERROR] 파일 읽기 실패: {e}")
            return None

        # 기존 process 호출
        return self.process(image_data, output_path)