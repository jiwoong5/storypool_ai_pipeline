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

    def extract_scene_info(self, scene: Dict[str, Any]) -> str:
        formatted = f"""
        - Scene Number: {scene.get('scene_number')}
        - Scene Title: {scene.get('scene_title')}
        - Characters: {', '.join(scene.get('characters', []))}
        - Location: {scene.get('location')}
        - Time: {scene.get('time') or 'None'}
        - Mood: {scene.get('mood')}
        - Summary: {scene.get('summary')}
        - Dialogue Count: {scene.get('dialogue_count')}
        """.strip()
        return formatted
    
    def save_prompts_json(self, results: List[Dict[str, Any]], filename: str):
        """생성된 프롬프트들을 JSON 파일로 저장합니다."""
        try:
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(results, f, indent=2, ensure_ascii=False, default=str)
            print(f"JSON 형태로 저장 완료 → {filename}")
        except Exception as e:
            print(f"JSON 파일 저장 중 오류 발생: {str(e)}")

    def process(self, input_path: str, output_path: str, save_json: bool = False) -> Dict[str, Any]:
        """장면 JSON 파일을 처리하여 프롬프트를 생성합니다."""
        try:
            # JSON 파일 로드
            scenes_raw_data = self.load_scenes_json(input_path)
            
            # scene_info (string) 리스트 준비
            scene_texts = []
            for scene in scenes_raw_data["scenes"]:
                scene_info = self.extract_scene_info(scene)
                scene_texts.append(scene_info)

            # make_prompts 로 프롬프트 생성
            results = self.prompt_maker.make_prompts(scene_texts)

            self.save_prompts_json(results, output_path)

            return {
                "prompts": results.get("prompts", []),
                "message": "Character-consistent image generation prompts created successfully"
            }
        
        except Exception as e:
            print(f"처리 중 오류 발생: {str(e)}")
            return {
                "prompts": [],
                "message": f"Processing failed: {str(e)}"
            }
            