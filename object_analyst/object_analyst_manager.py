import re
from object_analyst.object_analyst_interface import ObjectAnalysisInterface

class ObjectAnalystManager:
    def __init__(self, object_analyst: ObjectAnalysisInterface):
        self.object_analyst = object_analyst

    def load_text(self, filename: str) -> str:
        with open(filename, "r", encoding="utf-8") as f:
            return f.read()

    def save_result(self, result: str, filename: str):
        with open(filename, "w", encoding="utf-8") as f:
            f.write(result.strip())
            f.write("\n\n")

    def merge_scenes(self, text: str) -> str:
        merged = re.sub(r'Scene \d+:\s*', '', text)
        return merged.strip()

    def process(self, input_path: str, output_path: str):
        text = self.load_text(input_path)
        merged = self.merge_scenes(text)
        result = self.object_analyst.extract_objects(merged)

        self.save_result(result, output_path)
        print(f"모든 scene 등장인물 추출 완료 → {output_path} 저장됨")
