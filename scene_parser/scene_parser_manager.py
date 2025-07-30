import json

class SceneParserManager:
    def __init__(self, parser):
        self.parser = parser

    def load_text(self, filename: str) -> str:
        with open(filename, "r", encoding="utf-8") as f:
            return f.read()

    def save_scenes(self, scene_response_dict: dict, output_file: str):
        """Pydantic dict 형태의 scene_response를 JSON 파일로 저장"""
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(scene_response_dict, f, ensure_ascii=False, indent=2, default=str)

    def process(self, input_text: str):
        scene_response = self.parser.parse(input_text)
        return json.dumps(scene_response)

    def process_from_path(self, input_file: str, output_file: str):
            text = self.load_text(input_file)
            scene_response = self.parser.parse(text)  # Pydantic 모델
            
            # Pydantic dict 변환
            scene_response_dict = scene_response.dict()
            
            self.save_scenes(scene_response_dict, output_file)
            
            return scene_response