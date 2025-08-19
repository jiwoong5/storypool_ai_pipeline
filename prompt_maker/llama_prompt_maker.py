from prompt_maker.prompt_maker_interface import PromptMakerInterface
from llama_tools.llama_helper import LlamaHelper
from api_caller.api_caller_selector import APICallerSelector
from typing import Dict, List, Any
from util.json_maker import JsonMaker
import json, os

class LlamaPromptMaker(PromptMakerInterface):
    def __init__(self, model_name: str = "llama3.2:3b", api_url: str = None):
        from dotenv import load_dotenv
        load_dotenv()
        host = api_url or os.getenv("OLLAMA_HOST", "http://localhost:11434")
        self.api_url = host.rstrip("/") + "/api/generate"
        self.model_name = model_name
        self.llm_helper = LlamaHelper(
            call_api_fn=APICallerSelector.select("llama", model=model_name, api_url=self.api_url)
        )
        self.main_instruction = self._get_main_instruction()
        self.character_analysis_instruction = self._get_character_analysis_instruction()
        self.costume_analysis_instruction = self._get_costume_analysis_instruction()
        self.caution = self._get_caution()
        self.json_maker = JsonMaker()

        # 그림체 관련 문구
        self.art_style_text = "studio ghibli style, 2D hand-drawn animation, soft watercolor painting, delicate lineart, pastel color palette"

    def _get_character_analysis_instruction(self) -> str:
        return """
        You are an expert character analyst. Analyze the characters appearing in the story scenes and extract their consistent physical characteristics.

        ## Guidelines:
        - Extract characters from all scenes and identify their consistent physical traits
        - Focus on permanent features: hair , face shape, age/gender, body type, distinctive features
        - Do not include temporary elements like clothing or expressions
        - If the same character appears in multiple scenes, consolidate their information
        - Create character profiles that will ensure visual consistency across all scenes
        - Important: For the character_name field, use the value from the input format's characters field exactly as it is, without any modifications.


        ## Character Profile Fields:
        - **character_name**: Character identifier (use exact name from the story)
        - **age_group**: Child/teenager/young adult/middle-aged/elderly
        - **gender**: Male/female/other
        - **hair**: Color, style, length
        - **face**: Face shape, distinctive facial features
        - **body_type**: General body build
        - **distinctive_features**: Any unique physical characteristics

        ## input format:
        {
            "scenes": [
                {
                "scene_number": "",
                "characters": [],
                "time": "",
                "mood": "",
                "story": "",
                "dialogue_count": "",
                "location": ""
                }
            ],
            "total_scenes": "",
            "main_characters": [],
            "locations": []
        }

        ## Response Format:
        {
            "characters": [
                {
                    "character_name": "",
                    "age_group": "",
                    "gender": "",
                    "hair": "",
                    "face": "",
                    "body_type": "",
                    "distinctive_features": ""
                }
            ],
            "total_characters": 0
        }

        ## Please analyze characters from the following scenes:
        {scene_data}
        """

    def _get_costume_analysis_instruction(self) -> str:
            return """
            You are an expert costume and clothing analyst. Analyze the clothing and outfits of characters appearing in each scene.

            ## Guidelines:
            - Analyze clothing for each character in each scene separately
            - Focus on complete outfit descriptions that can be used directly in image generation prompts
            - If there is no prior physical description of the character in previous scenes, make a reasonable assumption based on the context of the story.
            - Keep descriptions concise but detailed enough for image generation
            - If the outfit remains the same between the previous scene and the current scene, the outfit_description can be left empty.
            - Outfit descriptions should only be written when it is the first time for the character or when the character's outfit has clearly changed.
            - Important: For the character_name field, use the value from the input format's characters field exactly as it is, without any modifications.

            ## input format:
            {
                "scenes": [
                    {
                    "scene_number": "",
                    "characters": [],
                    "time": "",
                    "mood": "",
                    "story": "",
                    "dialogue_count": "",
                    "location": ""
                    }
                ],
                "total_scenes": "",
                "main_characters": [],
                "locations": []
            }

            ## Response Format:
            {
                "scene_costumes": [
                    {
                        "scene_number": "",
                        "character_outfits": [
                            {
                                "character_name": "",
                                "outfit_description": ""
                            }
                        ]
                    }
                ],
                "total_scenes": ""
            }

            ## Please analyze costumes for each scene from the following:
            {scene_data}
            """
    
    def _get_main_instruction(self) -> str:
        return """
        You are an expert prompt engineer creating detailed, image generation prompts that focus on poses, actions, mood, background, environment, objects, and character-object relationships.

        ## Task:
        Transform scene data into prompts focusing on dynamic elements without describing character physical appearance.

        ## Guidelines:
        - Focus on poses, actions, expressions, and body language of characters
        - Detail background, environment, and setting elements
        - Include all key objects, props, and living beings mentioned in the story.
        - Describe interactions and relationships between characters and key objects, props, living beings.
        - DO NOT describe character physical appearance - these will be added later
        - Do not describe the character's clothing. - these will be added later

        ## Field Descriptions:
        - **scene_number**: A number representing the order of the scene in the story
        - **generated_prompt**: A detailed text description focusing on actions, poses, mood, environment, objects, and interactions (without character physical descriptions)

        ## Response Format (Example):
        {
            "prompts": [
                {
                    "scene_number": "1",
                    "generated_prompt": ""
                },
                {
                    "scene_number": "2", 
                    "generated_prompt": ""
                }
            ],
            "total_prompts": 2
        }

        ## Please write prompts based on the following scene data:
        {scene_data}
        """

    def _get_caution(self) -> str:
        return "Return only valid JSON format. Do not include any explanatory text before or after the JSON."

    def get_error_response(self, error_message: str, scene_index: int = None) -> dict:
        response = {
            "scene_number": scene_index if scene_index is not None else -1,
            "success": False,
            "message": f"Prompt generation failed: {error_message}",
            "generated_prompt": ""
        }
        return response

    def add_art_style_to_prompts(self, prompts: list) -> list:
        """각 프롬프트에 그림체 문구를 추가"""
        updated_prompts = []
        for p in prompts:
            # generated_prompt 필드가 있으면 뒤에 그림체 문구를 붙임
            if "generated_prompt" in p and isinstance(p["generated_prompt"], str):
                p["generated_prompt"] = p["generated_prompt"].strip() + ", " + self.art_style_text
            updated_prompts.append(p)
        return updated_prompts

    def add_character_descriptions_to_prompts(self, prompts: list, character_analysis: dict, costume_analysis: dict, scene_data: dict) -> list:
        """프롬프트 맨 앞에 캐릭터 묘사(외모 + 의상)를 추가하는 후처리 메서드"""
        updated_prompts = []
        
        # 캐릭터 분석 결과를 딕셔너리로 변환 (이름을 키로 사용)
        character_profiles = {}
        if "characters" in character_analysis:
            for char in character_analysis["characters"]:
                char_name = char.get('character_name', '').lower()
                char_desc = f"{char.get('age_group', '')}, {char.get('gender', '')}, {char.get('hair', '')}, {char.get('face', '')}, {char.get('body_type', '')}"
                if char.get('distinctive_features'):
                    char_desc += f", {char.get('distinctive_features', '')}"
                character_profiles[char_name] = char_desc.strip(', ')
        
        # 의상 분석 결과를 씬별로 정리
        costume_by_scene = {}
        if "scene_costumes" in costume_analysis:
            for scene_costume in costume_analysis["scene_costumes"]:
                scene_num = scene_costume.get("scene_number", "")
                costume_by_scene[scene_num] = {}
                for outfit in scene_costume.get("character_outfits", []):
                    char_name = outfit.get("character_name", "").lower()
                    outfit_desc = outfit.get("outfit_description", "")
                    costume_by_scene[scene_num][char_name] = outfit_desc
        
        # 각 씬의 프롬프트 처리
        scenes = scene_data.get("scenes", [])
        
        for i, prompt in enumerate(prompts):
            if "generated_prompt" in prompt and isinstance(prompt["generated_prompt"], str):
                scene_number = prompt.get("scene_number", str(i + 1))
                
                # 해당 씬의 캐릭터 정보 찾기
                current_scene = None
                for scene in scenes:
                    if str(scene.get("scene_number", "")) == str(scene_number):
                        current_scene = scene
                        break
                
                if current_scene and "characters" in current_scene:
                    # 씬에 등장하는 캐릭터들의 묘사 추가
                    character_descriptions = []
                    for char_name in current_scene["characters"]:
                        char_name_lower = char_name.lower()
                        
                        # 캐릭터 프로필에서 매칭되는 항목 찾기 (부분 매칭 포함)
                        matching_profile = None
                        for profile_name, profile_desc in character_profiles.items():
                            if char_name_lower in profile_name or profile_name in char_name_lower:
                                matching_profile = profile_desc
                                break
                        
                        # 해당 씬의 의상 정보 찾기
                        outfit_desc = ""
                        scene_costumes = costume_by_scene.get(scene_number, {})
                        for costume_name, costume_desc in scene_costumes.items():
                            if char_name_lower in costume_name or costume_name in char_name_lower:
                                outfit_desc = costume_desc
                                break
                        
                        # 캐릭터 묘사 조합 (외모 + 의상)
                        full_description = ""
                        if matching_profile:
                            full_description = matching_profile
                        if outfit_desc:
                            if full_description:
                                full_description += f", wearing {outfit_desc}"
                            else:
                                full_description = f"wearing {outfit_desc}"
                        
                        if full_description:
                            character_descriptions.append(f"{char_name} ({full_description})")
                        else:
                            character_descriptions.append(char_name)
                    
                    # 캐릭터 묘사를 프롬프트 맨 앞에 추가
                    if character_descriptions:
                        char_desc_text = ", ".join(character_descriptions) + "; "
                        prompt["generated_prompt"] = char_desc_text + prompt["generated_prompt"]
            
            updated_prompts.append(prompt)
        
        return updated_prompts

    def analyze_characters(self, scene_texts: List[str]) -> Dict[str, Any]:
        """등장인물 분석을 수행하는 메서드"""
        try:
            combined_scene_data = "\n\n".join(f"Scene {i+1}:\n{scene.strip()}" 
                                            for i, scene in enumerate(scene_texts))
            # 캐릭터 리스트 가져오기
            character_list_str =  "\n".join(str(c) for c in self._get_character_list(scene_texts))

            # 캐릭터 리스트를 문자열 끝에 추가
            combined_scene_data += f"\n\nCharacter list:\n{character_list_str}"
           
            character_instruction = self.character_analysis_instruction.replace(
                "{scene_data}",
                combined_scene_data
            )

            instruction = self.llm_helper.build_instruction(
                character_instruction,
                "",
                self.caution
            )

            result = self.llm_helper.retry_and_get_json(
                instruction,
                description="Character analysis from scenes"
            )

            return result

        except Exception as e:
            print(f"Character analysis failed: {e}")
            return {
                "characters": [],
                "total_characters": 0,
                "error": str(e)
            }

    def analyze_costumes(self, scene_texts: List[str]) -> Dict[str, Any]:
            """의상 분석을 수행하는 메서드"""
            try:
                combined_scene_data = "\n\n".join(f"Scene {i+1}:\n{scene.strip()}" for i, scene in enumerate(scene_texts))

                costume_instruction = self.costume_analysis_instruction.replace(
                    "{scene_data}",
                    combined_scene_data
                )

                instruction = self.llm_helper.build_instruction(
                    costume_instruction,
                    "",
                    self.caution
                )

                result = self.llm_helper.retry_and_get_json(
                    instruction,
                    description="Costume analysis from scenes"
                )
                return result

            except Exception as e:
                print(f"Costume analysis failed: {e}")
                return {
                    "scene_costumes": [],
                    "total_scenes": 0,
                    "error": str(e)
                }
            
    def fill_missing_costumes(self, costume_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        의상 분석 결과에서 비어있는 부분을 이전 씬의 의상으로 채우는 후처리 함수
        
        Args:
            costume_analysis: 의상 분석 결과 딕셔너리
        
        Returns:
            후처리된 의상 분석 결과
        """
        if not costume_analysis or "scene_costumes" not in costume_analysis:
            return costume_analysis
        
        scene_costumes = costume_analysis["scene_costumes"]
        if not scene_costumes:
            return costume_analysis
        
        # 캐릭터별 최신 의상 정보를 추적하는 딕셔너리
        character_last_outfits = {}
        
        # 씬 번호 순서대로 정렬 (문자열 숫자를 정수로 변환하여 정렬)
        try:
            scene_costumes.sort(key=lambda x: int(x.get("scene_number", "0")))
        except (ValueError, TypeError):
            # 숫자 변환이 실패하면 문자열 순서로 정렬
            scene_costumes.sort(key=lambda x: str(x.get("scene_number", "0")))
        
        # 각 씬을 순서대로 처리
        for scene_costume in scene_costumes:
            scene_number = scene_costume.get("scene_number", "")
            character_outfits = scene_costume.get("character_outfits", [])
            
            # 현재 씬의 캐릭터들과 의상 정보를 딕셔너리로 변환
            current_scene_outfits = {}
            for outfit in character_outfits:
                char_name = outfit.get("character_name", "").strip()
                outfit_desc = outfit.get("outfit_description", "").strip()
                if char_name:
                    current_scene_outfits[char_name.lower()] = {
                        "character_name": char_name,
                        "outfit_description": outfit_desc
                    }
            
            # 이전 씬의 의상 정보로 빈 부분 채우기
            updated_outfits = []
            
            # 현재 씬에 있는 캐릭터들 처리
            for char_name, outfit_info in current_scene_outfits.items():
                outfit_desc = outfit_info["outfit_description"]
                
                # 의상 정보가 비어있을 때 이전 scene 에서 가져오기
                if not outfit_desc:
                    if char_name in character_last_outfits:
                        # 이전 씬의 의상 복사
                        outfit_info["outfit_description"] = character_last_outfits[char_name]
                        print(f"Scene {scene_number}: Filled missing outfit for '{outfit_info['character_name']}' from previous scene")
                
                updated_outfits.append(outfit_info)
                
                # 현재 캐릭터의 최신 의상 정보 업데이트
                if outfit_info["outfit_description"] and outfit_info["outfit_description"].strip():
                    character_last_outfits[char_name] = outfit_info["outfit_description"]
            
            # 업데이트된 의상 정보로 교체
            scene_costume["character_outfits"] = updated_outfits
        return costume_analysis

    def analyze_costumes_with_postprocessing(self, scene_texts: List[str]) -> Dict[str, Any]:
        """
        의상 분석을 수행하고 후처리까지 포함하는 메서드
        
        Args:
            scene_texts: 씬 텍스트 리스트
        
        Returns:
            후처리된 의상 분석 결과
        """
        # 기본 의상 분석 수행
        costume_analysis = self.analyze_costumes(scene_texts)
        
        # 빈 의상 정보를 이전 씬에서 채우기
        costume_analysis = self.fill_missing_costumes(costume_analysis)
        
        return costume_analysis
    
    def _build_character_profiles_by_scene(self, scene_char_list: List[str], character_profiles: dict) -> dict:
        """
        scene_char_list의 prompts 정보를 기반으로 각 scene에 등장하는 캐릭터들의 profile을 붙여
        { scene_number: { character_name: profile } } 구조로 변환
        """
        scene_char_profiles = {}
        
        for scene_char in scene_char_list:
            scene_dict = scene_char
            scene_number = scene_dict.get("scene_number")
            scene_character_list = scene_dict.get("characters")

            scene_profiles = {}

            # character_profiles['characters']가 실제 캐릭터 리스트
            for char in character_profiles.get("characters", []):
                char_name = char["character_name"]
                char_name_lower = char_name.lower()
                scene_text_lower = [c.lower() for c in scene_character_list]

                if char_name_lower in scene_text_lower:
                    scene_profiles[char_name] = char

            if scene_number:
                scene_char_profiles[scene_number] = scene_profiles

        return scene_char_profiles

    def _build_costume_by_scene(self, costume_analysis: dict) -> dict:
        scene_costumes = {}
        if "scene_costumes" in costume_analysis:
            for scene_costume in costume_analysis["scene_costumes"]:
                scene_num = scene_costume.get("scene_number", "")
                scene_costumes[scene_num] = {}
                for outfit in scene_costume.get("character_outfits", []):
                    char_name = outfit.get("character_name", "").lower()
                    outfit_desc = outfit.get("outfit_description", "")
                    scene_costumes[scene_num][char_name] = outfit_desc
        return scene_costumes

    def _prepend_character_descriptions(
        self, 
        result: dict, 
        character_profiles_by_scene: dict,  # <-- 씬별 캐릭터 프로필
        costume_by_scene: dict              # <-- 씬별 의상 정보
    ) -> None:
        if not (isinstance(result, dict) and "prompts" in result):
            return

        for prompt in result["prompts"]:
            if "generated_prompt" not in prompt or not isinstance(prompt["generated_prompt"], str):
                continue
            
            scene_number = prompt.get("scene_number", "")
            scene_costumes = costume_by_scene.get(scene_number, {})
            scene_profiles = character_profiles_by_scene.get(scene_number, {})

            character_descriptions = []
            for char_name, char_desc in scene_profiles.items():
                outfit_desc = scene_costumes.get(char_name, "")
                full_description = char_desc
                if outfit_desc:
                    full_description += f", wearing {outfit_desc}"
                character_descriptions.append(f"{char_name} ({full_description})")
            
            if character_descriptions:
                char_desc_text = "; ".join(character_descriptions) + "; "
                prompt["generated_prompt"] = char_desc_text + prompt["generated_prompt"]

            # 최종 결과 출력
            print("Final generated_prompt:", prompt["generated_prompt"])

    def _get_character_list(self, scene_texts: List[str]):
        scene_char_list = []
        
        for i, scene_str in enumerate(scene_texts):
            
            # scene_str이 이미 딕셔너리인지 문자열인지 확인
            if isinstance(scene_str, str):
                try:
                    scene_dict = json.loads(scene_str)
                except json.JSONDecodeError as e:
                    print(f"Failed to parse scene string: {e}")
                    continue
            elif isinstance(scene_str, dict):
                scene_dict = scene_str
            else:
                continue
            
            scene_number = scene_dict.get("scene_number")
            characters = scene_dict.get("characters", [])
            
            scene_char_list.append({
                "scene_number": scene_number,
                "characters": characters
            })
        return scene_char_list
 
    def _get_unique_characters(self, scene_char_list: List[Dict[str, Any]]) -> List[str]:
        """
        모든 씬의 등장인물을 하나로 합쳐 중복 없이 반환
        """
        all_chars = []
        for scene in scene_char_list:
            all_chars.extend(scene.get("characters", []))
        
        # 순서 유지하면서 중복 제거
        unique_chars = list(dict.fromkeys(all_chars))
        return unique_chars
    
    def make_prompts(self, scene_texts: List[str]) -> List[Dict[str, Any]]:
        MAX_RETRIES = 3
        
        # 1. 등장인물 분석 (재시도 로직 포함)
        character_analysis = None
        character_number = len(self._get_unique_characters(self._get_character_list(scene_texts)))

        for attempt in range(MAX_RETRIES):
            try:
                print(f"Character analysis attempt {attempt + 1}/{MAX_RETRIES}")
                character_analysis = self.analyze_characters(scene_texts)
                
                # 타입 검증
                if not isinstance(character_analysis, dict):
                    raise TypeError(f"Character analysis returned {type(character_analysis)}, expected dict")
                
                if "characters" not in character_analysis:
                    raise ValueError("Character analysis missing 'characters' field")
                
                if not isinstance(character_analysis["characters"], list):
                    raise TypeError(f"Character analysis 'characters' is {type(character_analysis['characters'])}, expected list")
                
                actual_character_count = len(character_analysis["characters"])
                if actual_character_count != character_number:
                    raise ValueError(f"Character analysis mismatched: found {actual_character_count} characters (expected {character_number}")

                print(f"Character analysis successful: found {len(character_analysis['characters'])} characters")
                break
                
            except Exception as e:
                print(f"Character analysis attempt {attempt + 1} failed: {e}")
                if attempt == MAX_RETRIES - 1:
                    print("Character analysis failed after max retries, using empty result")
                    character_analysis = {"characters": [], "total_characters": 0}

        # 2. 등장인물 의상 분석 (재시도 로직 포함)
        costume_analysis = None
        for attempt in range(MAX_RETRIES):
            try:
                print(f"Costume analysis attempt {attempt + 1}/{MAX_RETRIES}")
                costume_analysis = self.analyze_costumes_with_postprocessing(scene_texts)
                
                # 타입 검증
                if not isinstance(costume_analysis, dict):
                    raise TypeError(f"Costume analysis returned {type(costume_analysis)}, expected dict")
                
                if "scene_costumes" not in costume_analysis:
                    raise ValueError("Costume analysis missing 'scene_costumes' field")
                
                if not isinstance(costume_analysis["scene_costumes"], list):
                    raise TypeError(f"Costume analysis 'scene_costumes' is {type(costume_analysis['scene_costumes'])}, expected list")
                
                # 개수 검증
                if len(costume_analysis["scene_costumes"]) != len(scene_texts):
                    raise ValueError(f"Costume analysis scene count mismatch: {len(costume_analysis['scene_costumes'])} != {len(scene_texts)}")
                
                print(f"Costume analysis successful: processed {len(costume_analysis['scene_costumes'])} scenes")
                break
                
            except Exception as e:
                print(f"Costume analysis attempt {attempt + 1} failed: {e}")
                if attempt == MAX_RETRIES - 1:
                    print("Costume analysis failed after max retries, using empty result")
                    costume_analysis = {
                        "scene_costumes": [{"scene_number": str(i+1), "character_outfits": []} for i in range(len(scene_texts))],
                        "total_scenes": len(scene_texts)
                    }

        # 3. 프롬프트 생성 (재시도 로직 포함)
        result = None
        for attempt in range(MAX_RETRIES):
            try:
                print(f"Prompt generation attempt {attempt + 1}/{MAX_RETRIES}")
                
                # 씬 데이터 준비
                combined_scene_data = "\n\n".join(f"Scene {i+1}:\n{scene.strip()}" for i, scene in enumerate(scene_texts))

                # 행동, 포즈, 분위기 중심의 프롬프트 생성
                prompt_instruction = self.main_instruction.replace("{scene_data}", combined_scene_data)

                instruction = self.llm_helper.build_instruction(
                    prompt_instruction,
                    "",
                    self.caution
                )

                result = self.llm_helper.retry_and_get_json(
                    instruction,
                    description="Action-focused image generation prompts"
                )
                
                # 타입 검증
                if not isinstance(result, dict):
                    raise TypeError(f"Prompt generation returned {type(result)}, expected dict")
                
                if "prompts" not in result:
                    raise ValueError("Prompt generation missing 'prompts' field")
                
                if not isinstance(result["prompts"], list):
                    raise TypeError(f"Prompt generation 'prompts' is {type(result['prompts'])}, expected list")
                
                # 개수 검증
                if len(result["prompts"]) != len(scene_texts):
                    raise ValueError(f"Prompt generation count mismatch: {len(result['prompts'])} != {len(scene_texts)}")
                
                # 각 프롬프트 구조 검증
                for i, prompt in enumerate(result["prompts"]):
                    if not isinstance(prompt, dict):
                        raise TypeError(f"Prompt {i} is {type(prompt)}, expected dict")
                    if "generated_prompt" not in prompt:
                        raise ValueError(f"Prompt {i} missing 'generated_prompt' field")
                    if not isinstance(prompt["generated_prompt"], str):
                        raise TypeError(f"Prompt {i} 'generated_prompt' is {type(prompt['generated_prompt'])}, expected str")
                
                print(f"Prompt generation successful: created {len(result['prompts'])} prompts")
                break
                
            except Exception as e:
                print(f"Prompt generation attempt {attempt + 1} failed: {e}")
                if attempt == MAX_RETRIES - 1:
                    print("Prompt generation failed after max retries, returning error responses")
                    return [self.get_error_response(str(e), idx) for idx in range(1, len(scene_texts) + 1)]

        # 4. 캐릭터 리스트 추출 (재시도 로직 포함)
        scene_char_list = None
        for attempt in range(MAX_RETRIES):
            try:
                print(f"Character list extraction attempt {attempt + 1}/{MAX_RETRIES}")
                scene_char_list = self._get_character_list(scene_texts)
                
                # 타입 검증
                if not isinstance(scene_char_list, list):
                    raise TypeError(f"Character list returned {type(scene_char_list)}, expected list")
                
                if len(scene_char_list) != len(scene_texts):
                    raise ValueError(f"Character list count mismatch: {len(scene_char_list)} != {len(scene_texts)}")
                
                print(f"Character list extraction successful: processed {len(scene_char_list)} scenes")
                break
                
            except Exception as e:
                print(f"Character list extraction attempt {attempt + 1} failed: {e}")
                if attempt == MAX_RETRIES - 1:
                    print("Character list extraction failed after max retries, using empty list")
                    scene_char_list = [{"scene_number": str(i+1), "characters": []} for i in range(len(scene_texts))]

        # 5. 캐릭터 프로필 구성 (재시도 로직 포함)
        character_profiles_by_scene = None
        for attempt in range(MAX_RETRIES):
            try:
                print(f"Character profiles building attempt {attempt + 1}/{MAX_RETRIES}")
                print(scene_char_list)
                print(character_analysis)
                character_profiles_by_scene = self._build_character_profiles_by_scene(scene_char_list, character_analysis)
                
                # 타입 검증
                if not isinstance(character_profiles_by_scene, dict):
                    raise TypeError(f"Character profiles by scene returned {type(character_profiles_by_scene)}, expected dict")
                
                print(f"Character profiles building successful: processed {len(character_profiles_by_scene)} scenes")
                break
                
            except Exception as e:
                print(f"Character profiles building attempt {attempt + 1} failed: {e}")
                if attempt == MAX_RETRIES - 1:
                    print("Character profiles building failed after max retries, using empty dict")
                    character_profiles_by_scene = {}

        # 6. 의상 정보 구성 (재시도 로직 포함)
        costume_by_scene = None
        for attempt in range(MAX_RETRIES):
            try:
                print(f"Costume by scene building attempt {attempt + 1}/{MAX_RETRIES}")
                costume_by_scene = self._build_costume_by_scene(costume_analysis)
                
                # 타입 검증
                if not isinstance(costume_by_scene, dict):
                    raise TypeError(f"Costume by scene returned {type(costume_by_scene)}, expected dict")
                
                print(f"Costume by scene building successful: processed {len(costume_by_scene)} scenes")
                break
                
            except Exception as e:
                print(f"Costume by scene building attempt {attempt + 1} failed: {e}")
                if attempt == MAX_RETRIES - 1:
                    print("Costume by scene building failed after max retries, using empty dict")
                    costume_by_scene = {}

        # 7. 캐릭터 묘사 추가 (재시도 로직 포함)
        for attempt in range(MAX_RETRIES):
            try:
                print(f"Character descriptions prepending attempt {attempt + 1}/{MAX_RETRIES}")
                self._prepend_character_descriptions(result, character_profiles_by_scene, costume_by_scene)
                print("Character descriptions prepending successful")
                break
                
            except Exception as e:
                print(f"Character descriptions prepending attempt {attempt + 1} failed: {e}")
                if attempt == MAX_RETRIES - 1:
                    print("Character descriptions prepending failed after max retries, continuing without character descriptions")

        # 8. 그림체 스타일 추가 (재시도 로직 포함)
        styled_prompts = None
        for attempt in range(MAX_RETRIES):
            try:
                print(f"Art style addition attempt {attempt + 1}/{MAX_RETRIES}")
                styled_prompts = self.add_art_style_to_prompts(result["prompts"])
                
                # 타입 검증
                if not isinstance(styled_prompts, list):
                    raise TypeError(f"Styled prompts returned {type(styled_prompts)}, expected list")
                
                if len(styled_prompts) != len(scene_texts):
                    raise ValueError(f"Styled prompts count mismatch: {len(styled_prompts)} != {len(scene_texts)}")
                
                print(f"Art style addition successful: processed {len(styled_prompts)} prompts")
                break
                
            except Exception as e:
                print(f"Art style addition attempt {attempt + 1} failed: {e}")
                if attempt == MAX_RETRIES - 1:
                    print("Art style addition failed after max retries, using original prompts")
                    styled_prompts = result["prompts"]

        # 최종 결과 반환
        try:
            final_result = {
                "prompts": styled_prompts,
                "total_prompts": len(styled_prompts)
            }
            
            # 최종 타입 검증
            if not isinstance(final_result, dict):
                raise TypeError(f"Final result is {type(final_result)}, expected dict")
            
            if "prompts" not in final_result or not isinstance(final_result["prompts"], list):
                raise ValueError("Final result missing or invalid 'prompts' field")
            
            print(f"Final result validation successful: returning {len(final_result['prompts'])} prompts")
            return final_result
            
        except Exception as e:
            print(f"Final result validation failed: {e}")
            return [self.get_error_response(str(e), idx) for idx in range(1, len(scene_texts) + 1)]