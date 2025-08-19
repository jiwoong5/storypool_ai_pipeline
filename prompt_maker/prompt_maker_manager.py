from prompt_maker.prompt_maker_interface import PromptMakerInterface
import json
from typing import List, Dict, Any

class PromptMakerManager:
    def __init__(self, prompt_maker: PromptMakerInterface):
        self.prompt_maker = prompt_maker

    def load_scenes_json(self, filename: str) -> Dict[str, Any]:
        """JSON 파일에서 장면 데이터를 로드합니다."""
        try:
            with open(filename, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"JSON 파일을 찾을 수 없습니다: {filename}")
        except json.JSONDecodeError as e:
            raise ValueError(f"JSON 파일 파싱 오류: {e}")

    def extract_scene_info(self, scene: Dict[str, Any]):
        """
        Scene dict를 받아서 JSON 호환 dict로 반환
        """
        return json.dumps(scene)

    
    def save_prompts_json(self, results: List[Dict[str, Any]], filename: str):
        """생성된 프롬프트들을 JSON 파일로 저장합니다."""
        try:
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(results, f, indent=2, ensure_ascii=False, default=str)
            print(f"JSON 형태로 저장 완료 → {filename}")
        except Exception as e:
            print(f"JSON 파일 저장 중 오류 발생: {str(e)}")

    def process(self, json_string: str):
        """JSON 문자열을 처리하여 프롬프트를 생성합니다."""
        try:
            # 문자열로부터 JSON 파싱
            scenes_raw_data = json.loads(json_string)

            # scene_info (string) 리스트 준비
            scene_texts = []
            for scene in scenes_raw_data["scenes"]:
                scene_info = self.extract_scene_info(scene)
                scene_texts.append(scene_info)

            # make_prompts 로 프롬프트 생성
            results = self.prompt_maker.make_prompts(scene_texts)
            return json.dumps(results.get("prompts", []))

        except Exception as e:
            print(f"[에러] 처리 중 예외 발생: {str(e)}")
            return {
                "prompts": [],
                "message": f"Processing failed: {str(e)}"
            }
        