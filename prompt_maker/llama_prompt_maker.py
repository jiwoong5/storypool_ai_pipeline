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
        self.caution = self._get_caution()
        self.json_maker = JsonMaker()

        # 그림체 관련 문구
        self.art_style_text = "studio ghibli style, 2D hand-drawn animation, soft watercolor painting, delicate lineart, pastel color palette"

    def _get_main_instruction(self) -> str:
        return """
        You are an expert prompt engineer creating detailed, image generation prompts that strictly maintain character consistency across all scenes.

        ## Task:
        Transform scene data into prompts emphasizing a consistent character (age, body, hair, clothing, expression) without using names.

        ## Guidelines:
        - Maintain the same appearance and outfit for all characters in every scene.
        - All characters and key objects mentioned in the story must appear in the prompt.
        - Interactions between the characters and key objects described in the story must be included in the prompt.
        - Each prompt must be written completely independently. Do not use expressions that refer to other scenes or previous/next scenes (e.g., "scene 1’s," "earlier," "previously").
        - For each scene, independently restate the characteristics of the characters.

        ## Field Descriptions:
        - **scene_number**: A number representing the order of the scene in the story.
        - **generated_prompt**: A detailed text description of the scene suitable for image generation, including all characters, key objects, their interactions, character expressions, and outfits. Avoid using character names.

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
            },
            {
            "scene_number": "3",
            "generated_prompt": ""
            }
        ],
        "total_prompts": 3
        }

        ## Please write prompts based on the following input
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
                p["generated_prompt"] = p["generated_prompt"].strip() + self.art_style_text
            updated_prompts.append(p)
        return updated_prompts

    def make_prompts(self, scene_texts: List[str]) -> List[Dict[str, Any]]:
        try:
            combined_scene_data = "\n\n".join(f"Scene {i+1}:\n{scene.strip()}" for i, scene in enumerate(scene_texts))

            combined_instruction = self.main_instruction.replace(
                "{scene_data}",
                combined_scene_data
            )

            instruction = self.llm_helper.build_instruction(
                combined_instruction,
                "",
                self.caution
            )

            result = self.llm_helper.retry_and_get_json(
                instruction,
                description="Batch scene image generation prompts"
            )

            # 프롬프트 생성 후 그림체 문구 추가
            if isinstance(result, dict) and "prompts" in result:
                result["prompts"] = self.add_art_style_to_prompts(result["prompts"])

            return result

        except Exception as e:
            print(f"Batch prompt generation failed: {e}")
            return [self.get_error_response(str(e), idx) for idx in range(1, len(scene_texts) + 1)]
