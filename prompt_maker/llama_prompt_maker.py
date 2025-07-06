from prompt_maker.prompt_maker_interface import PromptMakerInterface
from llama_tools.llama_helper import LlamaHelper
from api_caller.api_caller_selector import APICallerSelector
from typing import Dict, List, Any
from util.json_maker import JsonMaker
import json

class LlamaPromptMaker(PromptMakerInterface):
    def __init__(self, model_name: str = "llama3.2:3b", api_url: str = "http://localhost:11434/api/generate"):
        self.llm_helper = LlamaHelper(
            call_api_fn=APICallerSelector.select("llama", model=model_name, api_url=api_url)
        )
        self.main_instruction = self._get_main_instruction()
        self.caution = self._get_caution()
        self.json_maker = JsonMaker()

    def _get_main_instruction(self) -> str:
        return """You are an expert prompt engineer specializing in creating high-quality image generation prompts with strong emphasis on character consistency.

    ## Task:
    Transform provided scene data into a detailed, high-quality image generation prompt that **strictly maintains character consistency** across all scenes.

    ## Input Format (Example):
    - Scene Number: 1
    - Scene Title: Getting ready at home
    - Characters: ["young adult woman"]
    - Location: Bedroom
    - Time: Morning
    - Mood: Calm
    - Summary: A young woman is sitting on her bed, preparing for the day in soft morning light.
    - Dialogue Count: 0

    ## Guidelines:
    - ALWAYS describe the main character(s) using detailed, consistent physical features (age, build, hair, clothing, expression, posture).
    - NEVER use character names — use descriptive phrases (e.g., "slim young adult woman with shoulder-length brown hair").
    - ALL SCENES must describe the same main character(s) consistently in terms of appearance.
    - Focus on character appearance, pose, interaction, and prominence in the scene.
    - Include clear composition, lighting, mood, and style references.
    - Include technical quality keywords (e.g., ultra-detailed, 8K resolution, cinematic lighting).
    - Each prompt must be 150-300 characters long.
    - Response MUST be a valid JSON object exactly as shown below — **NO reasoning, no explanations, no extra text**.

    ## Response Format (Example):
    {
    "prompts": [
        {
        "scene_number": 1,
        "generated_prompt": "Soft storybook illustration of a slim young adult woman with shoulder-length brown hair wearing a cozy white t-shirt and distressed denim jeans, sitting peacefully on a bed against the wall in a warmly sunlit bedroom, natural morning light filtering softly through the window, gentle expression, watercolor texture, soft pastel colors, warm tones, ultra-detailed"
        },
        {
        "scene_number": 2,
        "generated_prompt": "Warm storybook illustration of the same slim young adult woman with shoulder-length brown hair wearing the same cozy white t-shirt and distressed denim jeans, sitting on a blanket beside a middle-aged woman with silver hair in a flowing yellow sundress in a sunny park, children playing in the background, soft warm light, watercolor texture, soft pastel colors, warm tones, ultra-detailed"
        },
        {
        "scene_number": 3,
        "generated_prompt": "Calm storybook illustration of the same slim young adult woman with shoulder-length brown hair wearing the same cozy white t-shirt and distressed denim jeans, walking beside her mother towards the park exit, both wearing happy expressions, gentle afternoon light casting a warm glow, watercolor texture, soft pastel colors, warm tones, ultra-detailed"
        }
    ],
    "total_prompts": 3
    }

    ## Please write prompts based on the following input
    {scene_data}
    """

    
    def _get_caution(self) -> str:
        return """CRITICAL CAUTIONS:
    1. ALWAYS respond in valid JSON format exactly as specified — no additional text or reasoning.
    2. Characters must be described consistently across ALL scenes: age, build, hair, clothing, expression, posture.
    3. DO NOT use character names — use descriptive phrases like "slim young adult woman with shoulder-length brown hair".
    4. Prompts must be 150-300 characters long.
    5. Include artistic style, composition, lighting, and technical quality keywords (e.g., ultra-detailed, 8K resolution).
    6. Ensure character positioning, interaction, and prominence are clear.
    7. Environmental elements must support and not overshadow the characters.
    8. DO NOT change the character’s physical description between scenes — this is critical."""

    def get_error_response(self, error_message: str, scene_index: int = None) -> dict:
            """
            에러 발생 시 일관된 JSON 형식으로 응답 반환.
            """
            response = {
                "scene_number": scene_index if scene_index is not None else -1,
                "success": False,
                "message": f"Prompt generation failed: {error_message}",
                "generated_prompt": ""
            }
            return response

    def make_prompts(self, scene_texts: List[str]) -> List[Dict[str, Any]]:
        """여러 scene 텍스트를 한 번에 받아 한꺼번에 프롬프트 생성"""
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

            return result

        except Exception as e:
            print(f"Batch prompt generation failed: {e}")
            return [self.get_error_response(str(e), idx) for idx in range(1, len(scene_texts) + 1)]
