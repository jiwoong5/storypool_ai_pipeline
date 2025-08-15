import re, os, json
from typing import List, Dict, Any
from api_responses.responses import SceneInfo, SceneParserResponse
from api_responses.responses import SceneParserResponse
from scene_parser.scene_parser_interface import SceneParserInterface
from llama_tools.llama_helper import LlamaHelper
from api_caller.api_caller_selector import APICallerSelector

class LlamaSceneParser(SceneParserInterface):
    """Llama 모델을 사용한 장면 파싱 클래스 (Location 추론 분리)"""
    
    def __init__(self, model_name: str = "llama3.2:3b", api_url: str = None):
        from dotenv import load_dotenv
        load_dotenv()
        host = api_url or os.getenv("OLLAMA_HOST", "http://localhost:11434")
        self.api_url = host.rstrip("/") + "/api/generate"
        self.model_name = model_name
        self.llm_helper = LlamaHelper(
            call_api_fn=APICallerSelector.select("llama", model=model_name, api_url=self.api_url),
        )

    def parse(self, text_content: str):
        """
        텍스트를 분석하여 장면별로 파싱하고 구조화된 결과를 반환
        
        Args:
            text_content (str): 분석할 텍스트 내용
            
        Returns:
            SceneParserResponse: 구조화된 장면 분석 결과 (Pydantic 모델)
        """
        try:
            # 1단계: 기본 장면 파싱 (location 제외)
            basic_scenes_data = self._parse_basic_scenes_with_retry(text_content)
            
            # 2단계: 장면별 location 추론
            locations = self._infer_locations(basic_scenes_data)
            
            # 3단계: location을 기본 장면 데이터에 추가
            enhanced_scenes_data = self._merge_locations(basic_scenes_data, locations)
            
            return enhanced_scenes_data
            
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

    def _parse_basic_scenes(self, text_content: str):
        """
        기본 장면 파싱 (location 제외)
        """
        main_instruction = '''
        You are a professional story analyst. Carefully read the given text and divide the story into distinct scenes at sentences where logical transitions occur. Then, accurately extract the key elements of each scene. If a sentence is ambiguous about which scene it belongs to, you may attach it to either the preceding or following scene.

        Criteria for dividing scenes:

        Sentence boundaries where a change of location occurs

        Sentence boundaries where the passage of time occurs

        Sentence boundaries where a change in main activity occurs

        Sentence boundaries where a change in characters occurs

        Description of each field:

        scene_number: Indicates the sequential order of the scene within the story.

        characters: Lists all characters who appear in the scene, identified by name.

        time: Denotes the time when the scene occurs, such as morning, afternoon, evening, or a specific time.

        mood: Describes the emotional tone or atmosphere of the scene.

        story: The story field of each scene should contain the exact excerpt from the original text corresponding to that scene. The exact sentences from the original text corresponding to the scene. If the story fields of all scenes are concatenated in order, the complete story should be fully reconstructable.

        dialogue_count: The number of instances of dialogue present in the scene.

        
            Expected Output Format:
            {
                "scenes": [
                    {
                    "scene_number": "1",
                    "scene_title": "",
                    "characters": [],
                    "time": "",
                    "mood": "",
                    "story": "",
                    "dialogue_count": ""
                    },
                    {
                    "scene_number": "2",
                    "scene_title": "",
                    "characters": [],
                    "time": "",
                    "mood": "",
                    "story": "",
                    "dialogue_count": ""
                    }
                ],
                "total_scenes": "2",
                "main_characters": []
            }
        '''

        caution = "Return only valid JSON format. Do not include any explanatory text before or after the JSON. and don't forget the 'scenes': "
        
        instruction = self.llm_helper.build_instruction(main_instruction, text_content, caution)
        return self.llm_helper.retry_and_get_json(instruction, description="기본 장면 분석")

    def _parse_basic_scenes_with_retry(self, text_content: str, max_retry: int = 3):
        """
        텍스트를 분석하여 장면별 기본 데이터를 생성하고,
        각 scene의 story를 합쳐 원본 story와 비교하여 불일치 시 LLM에게 개선을 요청

        Args:
            text_content (str): 분석할 텍스트 내용
            max_retry (int): 재시도 최대 횟수

        Returns:
            dict: 개선된 기본 장면 데이터 (scene 배열 포함)
        """
        retry_count = 0

        while retry_count < max_retry:
            try:
                # 1. 기본 장면 파싱
                basic_scenes_data = self._parse_basic_scenes(text_content)
                
                # 2. scene의 story를 순서대로 합쳐 전체 story 재생성
                reconstructed_story = " ".join([scene["story"] for scene in basic_scenes_data.get("scenes", [])])
                
                # 3. 원본 story와 비교
                original_story = text_content

                if reconstructed_story == original_story:
                    return basic_scenes_data
                else:
                    print(f"Story 불일치 발견, LLM에 개선 요청, 재시도 {retry_count + 1}/{max_retry}")
                    
                    # 4. LLM에게 개선 요청
                    improved_scenes_data = self._request_story_fix(
                        reconstructed_story=reconstructed_story,
                        original_story=original_story,
                        basic_scenes_data=basic_scenes_data
                    )

                    # 개선된 데이터를 사용
                    basic_scenes_data = improved_scenes_data
                    retry_count += 1

            except Exception as e:
                retry_count += 1
                print(f"기본 장면 파싱 오류, 재시도 {retry_count}/{max_retry}: {e}")
        
        # 최대 재시도 후에도 불일치 시 경고 후 반환
        print("Story 재구성 실패: 원본과 일치하지 않음")
        return basic_scenes_data


    def _request_story_fix(self, reconstructed_story: str, original_story: str, basic_scenes_data: dict):
        """
        scene별 story를 합쳐 만든 reconstructed_story가 원본과 불일치할 경우
        LLM에게 개선을 요청하여 story를 맞추도록 하는 함수

        Args:
            reconstructed_story (str): scene story를 합쳐 만든 이야기
            original_story (str): 원본 story
            basic_scenes_data (dict): 현재 scene별 데이터

        Returns:
            dict: 개선된 basic_scenes_data
        """
        # 1. LLM instruction 작성
        main_instruction = (
            "Please improve the scene-by-scene stories below so that they match the original story exactly. "
            "Each scene's story should preserve the original sentences and order, "
            "modifying the 'story' fields so that the reconstructed story becomes completely identical to the original story."
        )

        caution = "Always return in JSON format, including the entire basic_scenes_data with the modified 'story' fields for each scene."

        # 2. LLM 호출을 위해 context 구성
        text_content = text_content = json.dumps({
            "reconstructed_story": reconstructed_story,
            "original_story": original_story,
            "basic_scenes_data": basic_scenes_data
        }, ensure_ascii=False)

        instruction = self.llm_helper.build_instruction(main_instruction, text_content, caution)

        # 3. LLM에게 재요청
        improved_scenes_data = self.llm_helper.retry_and_get_json(instruction, description="story 개선 요청")

        return improved_scenes_data

    def _infer_locations(self, basic_scenes_data: Dict[str, Any]):
        """
        장면별 story 내용을 기반으로 각 장면의 location 추론
        """
        try:
            # 장면별 요약 정보 생성
            scene_summaries = []
            scenes = basic_scenes_data.get("scenes", [])
            
            for i, scene in enumerate(scenes, 1):
                summary = f"Scene {i}: {scene.get('story', '')}"
                scene_summaries.append(summary)
            
            # 전체 장면 요약을 하나의 문자열로 결합
            scenes_context = "\n\n".join(scene_summaries)
            
            # location 추론 요청
            locations_str = self._request_location_inference(scenes_context, len(scenes))
            
            # LLM 반환 문자열을 실제 리스트로 변환
            locations = json.loads(locations_str)
            
            return locations
            
        except Exception as e:
            print(f"위치 추론 중 오류 발생: {e}")
            # 오류 발생 시 기본값으로 처리
            scenes_count = len(basic_scenes_data.get("scenes", []))
            return ["알 수 없음"] * scenes_count

    def _request_location_inference(self, scenes_context: str, scene_count: int):
        """
        전체 장면 컨텍스트를 고려하여 각 장면의 location 추론 요청
        """
        location_instruction = f'''
        You are a location inference expert. You will receive scene summaries from a story and need to infer the most appropriate location for each scene.

        Analyze the full context of all scenes and determine where each scene takes place. Consider the following:

        1. Character actions and dialogue within each scene
        2. Environmental clues and descriptions
        3. The overall story flow and character movements between scenes
        4. Time progression and setting changes
        5. Logical connections between scenes

        Output:
        An array of size N containing the main location for each of the N scenes

        Expected output format:
        ["", "", "", ...]
        '''

        caution = f"Return only valid array format with locations array. Do not include any explanatory text before or after the array."
        
        instruction = self.llm_helper.build_instruction(location_instruction, scenes_context, caution)
        return self.llm_helper.retry_and_extract(instruction, description="장면별 위치 추론")

    def _merge_locations(self, basic_scenes_data: Dict[str, Any], locations: List[str]):
        """
        기본 장면 데이터에 location 정보를 추가하여 최종 결과 생성
        """
        scenes = basic_scenes_data.get("scenes", [])
        
        # 각 장면에 location 추가
        for i, scene in enumerate(scenes):
            if i < len(locations):
                scene["location"] = locations[i]
            else:
                scene["location"] = "알 수 없음"
        
        return basic_scenes_data