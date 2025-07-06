import re
from typing import List, Dict, Any
from api_responses.responses import SceneInfo, SceneParserResponse
from api_responses.responses import SceneParserResponse
from scene_parser.scene_parser_interface import SceneParserInterface
from llama_tools.llama_helper import LlamaHelper
from api_caller.api_caller_selector import APICallerSelector

class ScenePostProcessor:
    """장면 데이터 후처리를 담당하는 클래스"""
    
    def __init__(self):
        self.common_characters = {
            "화자", "나", "주인공", "엄마", "아빠", "어머니", "아버지", 
            "mom", "mother", "dad", "father", "sister", "brother",
            "narrator", "I", "me"
        }
        
    def normalize_character_names(self, characters: List[str]) -> List[str]:
        """
        등장인물 이름 정규화
        
        Args:
            characters (List[str]): 정규화할 등장인물 목록
            
        Returns:
            List[str]: 정규화된 등장인물 목록
        """
        if not characters:
            return []
            
        normalized = []
        for char in characters:
            if not char:
                continue
                
            # 공백 제거
            char = char.strip()
            if not char:
                continue
                
            # 특수 문자가 포함된 이름 처리 (예: "F U")
            if len(char) <= 3 and any(c.isupper() for c in char):
                normalized.append(char)
            elif char.lower() in [c.lower() for c in self.common_characters]:
                # 공통 캐릭터명 정규화
                normalized.append(char.title())
            else:
                normalized.append(char.title())
                
        return list(set(normalized))  # 중복 제거
    
    def validate_scene_number(self, scenes: List[Dict]) -> List[Dict]:
        """
        장면 번호 검증 및 수정
        
        Args:
            scenes (List[Dict]): 검증할 장면 목록
            
        Returns:
            List[Dict]: 번호가 수정된 장면 목록
        """
        for i, scene in enumerate(scenes):
            scene['scene_number'] = i + 1
        return scenes
    
    def extract_main_characters_and_locations(self, scenes: List[SceneInfo]) -> tuple:
        """
        전체 장면에서 주요 등장인물과 장소 추출
        
        Args:
            scenes (List[SceneInfo]): 분석할 장면 목록
            
        Returns:
            tuple: (주요 등장인물 목록, 고유 장소 목록)
        """
        all_characters = []
        all_locations = []
        
        for scene in scenes:
            if scene.characters:
                all_characters.extend(scene.characters)
            if scene.location:
                all_locations.append(scene.location)
        
        # 빈도 기반으로 주요 등장인물 선별 (1회 이상 등장)
        char_counts = {}
        for char in all_characters:
            if char:
                char_counts[char] = char_counts.get(char, 0) + 1
        
        main_characters = [char for char, count in char_counts.items() if count >= 1]
        unique_locations = list(set([loc for loc in all_locations if loc]))
        
        return main_characters, unique_locations
    
    def validate_dialogue_count(self, dialogue_count: Any) -> int:
        """
        대화 수 검증 및 정규화
        
        Args:
            dialogue_count (Any): 검증할 대화 수
            
        Returns:
            int: 정규화된 대화 수
        """
        if dialogue_count is None:
            return 0
        if isinstance(dialogue_count, str):
            try:
                # 문자열에서 숫자 추출
                numbers = re.findall(r'\d+', dialogue_count)
                return int(numbers[0]) if numbers else 0
            except:
                return 0
        try:
            return max(0, int(dialogue_count))
        except:
            return 0
    
    def create_scene_info_from_dict(self, scene_data: Dict) -> SceneInfo:
        """
        딕셔너리에서 SceneInfo Pydantic 모델 생성
        
        Args:
            scene_data (Dict): 장면 데이터 딕셔너리
            
        Returns:
            SceneInfo: 생성된 SceneInfo 모델
        """
        # 등장인물 정규화
        characters = self.normalize_character_names(
            scene_data.get('characters', [])
        )
        
        # 대화 수 검증
        dialogue_count = self.validate_dialogue_count(
            scene_data.get('dialogue_count')
        )
        
        return SceneInfo(
            scene_number=scene_data.get('scene_number', 1),
            scene_title=scene_data.get('scene_title', '').strip() or None,
            characters=characters,
            location=scene_data.get('location', '').strip() or None,
            time=scene_data.get('time', '').strip() or None,
            mood=scene_data.get('mood', '').strip() or None,
            summary=scene_data.get('summary', '').strip() or None,
            dialogue_count=dialogue_count
        )
    
    def process_response(self, data: Dict) -> SceneParserResponse:
        """
        LLM 응답 데이터를 처리하여 SceneParserResponse 생성
        
        Args:
            data (Dict): 처리할 응답 데이터
            
        Returns:
            SceneParserResponse: 처리된 장면 파싱 응답
        """
        scenes_data = data.get('scenes', [])
        if not isinstance(scenes_data, list):
            scenes_data = []

        scenes_data = self.validate_scene_number(scenes_data)

        processed_scenes = []
        for scene_data in scenes_data:
            if not isinstance(scene_data, dict):
                continue
            try:
                scene_info = self.create_scene_info_from_dict(scene_data)
                processed_scenes.append(scene_info)
            except Exception as e:
                print(f"장면 생성 중 오류: {e}")
                continue

        main_characters, locations = self.extract_main_characters_and_locations(processed_scenes)

        return SceneParserResponse(
            status="success",
            message="장면 분석 완료",
            scenes=processed_scenes,
            total_scenes=len(processed_scenes),
            main_characters=self.normalize_character_names(main_characters),
            locations=locations
        )
    
class LlamaSceneParser(SceneParserInterface):
    """Llama 모델을 사용한 장면 파싱 클래스"""
    
    def __init__(self, model: str = "llama3.2:3b", api_url: str = "http://localhost:11434/api/generate"):
        """
        Args:
            model (str): 사용할 Llama 모델
            api_url (str): API 엔드포인트 URL
        """
        self.llm_helper = LlamaHelper(
            call_api_fn=APICallerSelector.select("llama", model=model, api_url=api_url),
        )
        self.post_processor = ScenePostProcessor()

    def parse(self, text_content: str) -> SceneParserResponse:
        """
        텍스트를 분석하여 장면별로 파싱하고 구조화된 결과를 반환
        
        Args:
            text_content (str): 분석할 텍스트 내용
            
        Returns:
            SceneParserResponse: 구조화된 장면 분석 결과 (Pydantic 모델)
        """
        main_instruction = '''You are a professional story analyst. Your task is to carefully read the given text, logically divide it into scenes, and accurately extract the key elements of each scene.

        Please follow these steps in your analysis:
        1. First, read the entire story and identify the scene transition points.
        2. For each scene, analyze and extract the characters, location, time, and mood.
        3. If there is dialogue, count the number of dialogue instances.
        4. Summarize each scene in one sentence.
        5. Specify the character index range (0-based) where the scene appears in the full text. Provide:
        - start_char: starting character index (inclusive)
        - end_char: ending character index (exclusive)

        Criteria for dividing scenes:
        - Change of location (e.g., moving from home to the park)
        - Passage of time (e.g., from morning to afternoon)
        - Change of main activity (e.g., walking → playing → eating)
        - Change in characters

        IMPORTANT: Return ONLY valid JSON format without any additional text or explanation.

        Example Output Format:
        {
        "scenes": [
            {
            "scene_number": 1,
            "scene_title": "Getting ready at home",
            "characters": ["Narrator"],
            "location": "Home",
            "time": "Morning",
            "mood": "Calm",
            "summary": "I finished getting ready at home in the morning to go to the park.",
            "dialogue_count": 0,
            "start_char": 0,
            "end_char": 123
            }
        ],
        "total_scenes": 1,
        "main_characters": ["Narrator"],
        "locations": ["Home"]
        }

        ---
        Response Format:
        ---'''

        caution = "Return only valid JSON format. Do not include any explanatory text before or after the JSON."
        
        try:
            instruction = self.llm_helper.build_instruction(main_instruction, text_content, caution)
            # LlamaHelper의 retry_and_get_json이 내부적으로 JsonMaker를 사용하여 JSON 처리
            raw_data = self.llm_helper.retry_and_get_json(instruction, description="장면 분석")
            # ScenePostProcessor는 이제 비즈니스 로직(정규화, 검증 등)만 처리
            processed_result = self.post_processor.process_response(raw_data)
            return processed_result
            
        except Exception as e:
            print(f"장면 파싱 중 오류 발생: {e}")
            return SceneParserResponse(
                status="error",
                message=f"장면 파싱 중 오류 발생: {str(e)}",
                scenes=[],
                total_scenes=0,
                main_characters=[],
                locations=[]
            )
    
    def parse_raw(self, text_content: str) -> str:
        """
        후처리 없이 원본 LLM 응답을 반환 (디버깅용)
        
        Args:
            text_content (str): 분석할 텍스트 내용
            
        Returns:
            str: 원본 LLM 응답
        """
        main_instruction = '''You are a professional story analyst. Your task is to carefully read the given text, logically divide it into scenes, and accurately extract the key elements of each scene.

        Please follow these steps in your analysis:
        1. First, read the entire story and identify the scene transition points.
        2. For each scene, analyze and extract the characters, location, time, and mood.
        3. If there is dialogue, count the number of dialogue instances.
        4. Summarize each scene in one sentence.

        Criteria for dividing scenes:
        - Change of location (e.g., moving from home to the park)
        - Passage of time (e.g., from morning to afternoon)
        - Change of main activity (e.g., walking → playing → eating)
        - Change in characters

        IMPORTANT: Return ONLY valid JSON format without any additional text or explanation.

        ---
        Response Format:
        ---'''

        caution = "Return only valid JSON format. Do not include any explanatory text before or after the JSON."
        instruction = self.llm_helper.build_instruction(main_instruction, text_content, caution)
        return self.llm_helper.retry_and_extract(instruction, description="장면 분석")