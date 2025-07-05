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

    def extract_scene_info(self, scene_data: Dict[str, Any]) -> str:
        result = []
        for scene in scene_data["scenes"]:
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
                result.append(formatted)
        return result
    
    def generate_prompts(self, scenes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """장면 데이터로부터 프롬프트들을 생성합니다."""
        results = []
        
        for i, scene_data in enumerate(scenes, start=1):
            try:
                scene_text = self.extract_scene_info(scene_data)
                scene_number = i
                
                # 기본 make_prompt 메소드 사용
                prompt = self.prompt_maker.make_prompt(scene_text, scene_number)
                result = {
                    'scene_index': scene_number,
                    'success': True,
                    'message': 'Generated successfully',
                    'generated_prompt': prompt,
                    'metadata': {}
                }
                
                results.append(result)
                print(f"Scene {scene_number} 처리 완료")
                
            except Exception as e:
                print(f"Scene {i} 처리 중 오류 발생: {str(e)}")
                results.append({
                    'scene_index': i,
                    'success': False,
                    'message': f'Error: {str(e)}',
                    'generated_prompt': '',
                    'metadata': {}
                })
        
        return results

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
            
            scenes_formatted_data = self.extract_scene_info(scenes_raw_data)

            # 프롬프트 생성
            results = self.generate_prompts(scenes_formatted_data)
            
            # 프롬프트 저장
            self.save_prompts_json(results, output_path)
            
            scenes_data = list(range(1, len(results) + 1))
            return {
                'results': results,
                'scenes_data': scenes_data
            }
            
        except Exception as e:
            print(f"처리 중 오류 발생: {str(e)}")
            return {
                'results': [],
                'scenes_data': {},
                'error': str(e)
            }

        """통계 정보를 출력합니다."""
        print("\n" + "="*50)
        print("프롬프트 생성 통계")
        print("="*50)
        print(f"전체 장면 수: {statistics.get('total_count', 0)}")
        print(f"성공한 장면 수: {statistics.get('success_count', 0)}")
        print(f"실패한 장면 수: {statistics.get('failure_count', 0)}")
        print(f"성공률: {statistics.get('success_rate', 0.0):.2%}")
        
        if 'average_quality_score' in statistics:
            print(f"평균 품질 점수: {statistics['average_quality_score']:.3f}")
        
        if 'average_prompt_length' in statistics:
            print(f"평균 프롬프트 길이: {statistics['average_prompt_length']:.1f}자")
        
        print("="*50)

        