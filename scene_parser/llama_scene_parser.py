import re, os
from typing import List, Dict, Any
from api_responses.responses import SceneInfo, SceneParserResponse
from api_responses.responses import SceneParserResponse
from scene_parser.scene_parser_interface import SceneParserInterface
from llama_tools.llama_helper import LlamaHelper
from api_caller.api_caller_selector import APICallerSelector

class LlamaSceneParser(SceneParserInterface):
    """Llama 모델을 사용한 장면 파싱 클래스"""
    
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
        main_instruction = '''You are a professional story analyst. Your task is to carefully read the given text, logically divide it into scenes, and accurately extract the key elements of each scene.

        Please follow these steps in your analysis:
        1. First, read the entire story and identify the scene transition points.
        2. For each scene, analyze and extract the characters, location, time, mood, and part of story.
        3. If there is dialogue, count the number of dialogue instances.
        4. sum of part of story must include full story.

        Criteria for dividing scenes:
        - Change of location (e.g., moving from home to the park)
        - Passage of time (e.g., from morning to afternoon)
        - Change of main activity (e.g., walking → playing → eating)
        - Change in characters

        IMPORTANT: Return ONLY valid JSON format without any additional text or explanation.

        Example Input:
        
        Emma woke up early in the morning. She looked out the window and sighed—it was a sunny day, but she felt strangely down.

        After having a quick breakfast, she grabbed her sketchbook and walked to the nearby park. Children were playing, dogs were running, and couples were talking on benches.

        She found a quiet bench under a tree and started drawing. A little girl came up to her and asked, “What are you drawing?” Emma smiled and showed her the sketch.

        Expected Output Format:
        {
        "scenes": [
            {
            "scene_number": 1,
            "scene_title": "Getting ready at home",
            "characters": ["Emma"],
            "location": "Home",
            "time": "Morning",
            "mood": "Melancholic",
            "story": "Emma woke up early in the morning. She looked out the window and sighed—it was a sunny day, but she felt strangely down.",
            "dialogue_count": 0
            },
            {
            "scene_number": 2,
            "scene_title": "Just arrived at the park",
            "characters": ["Emma", "dog", "couple", "children"],
            "location": "Park",
            "time": "Late Morning",
            "mood": "Peaceful",
            "story": "After having a quick breakfast, she grabbed her sketchbook and walked to the nearby park. Children were playing, dogs were running, and couples were talking on benches.",
            "dialogue_count": 0
            },
            {
            "scene_number": 3,
            "scene_title": "Sketching at the park",
            "characters": ["Emma", "Little girl"],
            "location": "Park",
            "time": "Late Morning",
            "mood": "Peaceful",
            "story": "She found a quiet bench under a tree and started drawing. A little girl came up to her and asked, “What are you drawing?” Emma smiled and showed her the sketch.",
            "dialogue_count": 1
            }
        ],
        "total_scenes": 2,
        "main_characters": ["Emma"],
        "locations": ["Home", "Park"]
        }

        ---
        Response Format:
        ---'''

        caution = "Return only valid JSON format. Do not include any explanatory text before or after the JSON."
        
        try:
            instruction = self.llm_helper.build_instruction(main_instruction, text_content, caution)
            # LlamaHelper의 retry_and_get_json이 내부적으로 JsonMaker를 사용하여 JSON 처리
            return self.llm_helper.retry_and_get_json(instruction, description="장면 분석")
            
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