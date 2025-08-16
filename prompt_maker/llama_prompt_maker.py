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

        ## Character Profile Fields:
        - **character_name**: Character identifier
        - **age_group**: Child/teenager/young adult/middle-aged/elderly
        - **gender**: Male/female/other
        - **hair**: Color, style, length
        - **face**: Face shape, distinctive facial features
        - **body_type**: General body build
        - **distinctive_features**: Any unique physical characteristics

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
            - Include clothing items, colors, materials, styles, and accessories
            - Consider the context, setting, and time period
            - If a character's outfit is not described in a scene, make reasonable assumptions based on the story context
            - Keep descriptions concise but detailed enough for image generation

            ## Response Format:
            {
                "scene_costumes": [
                    {
                        "scene_number": "1",
                        "character_outfits": [
                            {
                                "character_name": "",
                                "outfit_description": ""
                            }
                        ]
                    },
                    {
                        "scene_number": "2", 
                        "character_outfits": [
                            {
                                "character_name": "",
                                "outfit_description": ""
                            }
                        ]
                    }
                ],
                "total_scenes": 0
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
        - Describe mood, atmosphere, and emotional tone of the scene
        - Detail background, environment, and setting elements
        - Include all key objects and props mentioned in the story
        - Describe interactions and relationships between characters and objects
        - Include location, time, lighting, and environmental conditions
        - Each prompt must be written completely independently
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
            combined_scene_data = "\n\n".join(f"Scene {i+1}:\n{scene.strip()}" for i, scene in enumerate(scene_texts))

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
    
    def make_prompts_with_parsed_scenes(self, parsed_scenes: Dict[str, Any]) -> List[Dict[str, Any]]:
        """파싱된 씬 데이터를 사용하여 프롬프트를 생성하는 메서드"""
        try:
            # 1. 등장인물 분석을 위한 씬 텍스트 준비
            scene_texts = []
            for scene in parsed_scenes.get("scenes", []):
                scene_text = f"Scene {scene.get('scene_number', '')}: {scene.get('scene_title', '')}\n"
                scene_text += f"Characters: {', '.join(scene.get('characters', []))}\n"
                scene_text += f"Location: {scene.get('location', '')}\n"
                scene_text += f"Time: {scene.get('time', '')}\n"
                scene_text += f"Mood: {scene.get('mood', '')}\n"
                scene_text += f"Story: {scene.get('story', '')}"
                scene_texts.append(scene_text)

            # 2. 등장인물 분석
            character_analysis = self.analyze_characters(scene_texts)
            
            # 3. 의상 분석
            costume_analysis = self.analyze_costumes_with_postprocessing(scene_texts)
            
            # 4. 씬 데이터를 문자열로 변환 (캐릭터 물리적 묘사 제외)
            scene_data_text = ""
            for scene in parsed_scenes.get("scenes", []):
                scene_data_text += f"Scene {scene.get('scene_number', '')}:\n"
                scene_data_text += f"Title: {scene.get('scene_title', '')}\n"
                scene_data_text += f"Characters: {', '.join(scene.get('characters', []))}\n"
                scene_data_text += f"Location: {scene.get('location', '')}\n"
                scene_data_text += f"Time: {scene.get('time', '')}\n"
                scene_data_text += f"Mood: {scene.get('mood', '')}\n"
                scene_data_text += f"Story: {scene.get('story', '')}\n"
                scene_data_text += f"Dialogue Count: {scene.get('dialogue_count', '')}\n\n"

            # 5. 행동, 포즈, 분위기 중심의 프롬프트 생성
            prompt_instruction = self.main_instruction.replace("{scene_data}", scene_data_text)

            instruction = self.llm_helper.build_instruction(
                prompt_instruction,
                "",
                self.caution
            )

            result = self.llm_helper.retry_and_get_json(
                instruction,
                description="Action-focused image generation prompts"
            )

            # 6. 캐릭터 묘사를 프롬프트 앞에 추가 (후처리) - 이제 costume_analysis 전달
            if isinstance(result, dict) and "prompts" in result:
                result["prompts"] = self.add_character_descriptions_to_prompts(
                    result["prompts"], character_analysis, costume_analysis, parsed_scenes
                )
                
                # 7. 그림체 스타일 추가
                result["prompts"] = self.add_art_style_to_prompts(result["prompts"])

            return result

        except Exception as e:
            print(f"Prompt generation with parsed scenes failed: {e}")
            scene_count = len(parsed_scenes.get("scenes", []))
            return [self.get_error_response(str(e), idx) for idx in range(1, scene_count + 1)]
        
    def _build_character_profiles(self, character_analysis: dict) -> dict:
        profiles = {}
        if "characters" in character_analysis:
            for char in character_analysis["characters"]:
                char_name = char.get('character_name', '').lower()
                char_desc = f"{char.get('age_group', '')}, {char.get('gender', '')}, {char.get('hair', '')}, {char.get('face', '')}, {char.get('body_type', '')}"
                if char.get('distinctive_features'):
                    char_desc += f", {char.get('distinctive_features', '')}"
                profiles[char_name] = char_desc.strip(', ')
        return profiles

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

    def _prepend_character_descriptions(self, result: dict, character_profiles: dict, costume_by_scene: dict) -> None:
        if not (isinstance(result, dict) and "prompts" in result):
            return

        for prompt in result["prompts"]:
            if "generated_prompt" not in prompt or not isinstance(prompt["generated_prompt"], str):
                continue
            
            scene_number = prompt.get("scene_number", "")
            scene_costumes = costume_by_scene.get(scene_number, {})
            
            character_descriptions = []
            for char_name, char_desc in character_profiles.items():
                outfit_desc = ""
                for costume_char_name, costume_desc in scene_costumes.items():
                    if char_name in costume_char_name or costume_char_name in char_name:
                        outfit_desc = costume_desc
                        break
                full_description = char_desc
                if outfit_desc:
                    full_description += f", wearing {outfit_desc}"
                character_descriptions.append(f"{char_name} ({full_description})")
            
            if character_descriptions:
                char_desc_text = "; ".join(character_descriptions) + "; "
                prompt["generated_prompt"] = char_desc_text + prompt["generated_prompt"]

    def make_prompts(self, scene_texts: List[str]) -> List[Dict[str, Any]]:
        try:
            # 1. 등장인물 분석
            character_analysis = self.analyze_characters(scene_texts)
            
            # 2. 등장인물 의상 분석
            costume_analysis = self.analyze_costumes_with_postprocessing(scene_texts)

            # 3. 씬 데이터 준비
            combined_scene_data = "\n\n".join(f"Scene {i+1}:\n{scene.strip()}" for i, scene in enumerate(scene_texts))

            # 4. 행동, 포즈, 분위기 중심의 프롬프트 생성
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

            # 5. 캐릭터 묘사를 프롬프트 앞에 추가 (후처리)
            if isinstance(result, dict) and "prompts" in result:
                character_profiles = self._build_character_profiles(character_analysis)
                costume_by_scene = self._build_costume_by_scene(costume_analysis)
                self._prepend_character_descriptions(result, character_profiles, costume_by_scene)
                
                # 6. 그림체 스타일 추가
                result["prompts"] = self.add_art_style_to_prompts(result["prompts"])

            return result

        except Exception as e:
            print(f"Batch prompt generation failed: {e}")
            return [self.get_error_response(str(e), idx) for idx in range(1, len(scene_texts) + 1)]