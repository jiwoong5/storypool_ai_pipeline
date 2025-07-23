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
        return """You are an expert prompt engineer creating detailed, high-quality image generation prompts that strictly maintain character consistency across all scenes.

        ## Task:
        Transform scene data into storybook-style prompts emphasizing a consistent character (age, body, hair, clothing, expression) without using names.

        ## Guidelines:
        - Maintain the same character appearance and outfit in every scene; no changes unless explicitly instructed.
        - Use descriptive phrases like “slim young woman with shoulder-length brown hair”.
        - Emphasize a magical, dreamy, emotional tone with fairytale keywords (enchanted, whimsical, pastel, gentle, glowing).
        - Include classic children's illustration styles: watercolor, gouache, pencil sketch.
        - Focus on character expression, mood, interaction, and atmosphere.
        - Prompts must be 150–300 characters.
        - Output only valid JSON in this format — no explanations or extra text.

        ## Response Format (Example):
        {
        "prompts": [
            {
            "scene_number": 1,
            "generated_prompt": "Dreamy storybook illustration of a delicate young woman with flowing brown hair wearing a soft linen nightdress, gazing out a misty window in a cozy attic room, morning light gently pouring through enchanted curtains, watercolor texture, pastel hues, magical mood"
            },
            {
            "scene_number": 2,
            "generated_prompt": "Whimsical storybook illustration of the same gentle young woman, now changed out of her nightdress into a pale cotton blouse and soft skirt, sitting beneath a blooming cherry tree beside an older woman with silvery hair and warm eyes, petals drifting in the breeze, soft glowing sunlight, watercolor style, pastel tones"
            },
            {
            "scene_number": 3,
            "generated_prompt": "Fairytale-style storybook illustration of the same young woman, still dressed in her pale cotton blouse and soft skirt, walking hand-in-hand with her mother through a sun-dappled forest path, both smiling softly as golden light filters through the trees, watercolor texture, enchanted atmosphere, pastel colors, gentle mood"
            }
        ],
        "total_prompts": 3
        }

        ## Please write prompts based on the following input
        {scene_data}
    """

    
    def _get_caution(self) -> str:
        return """CRITICAL CAUTIONS:
        1. ALWAYS respond in valid JSON format exactly as specified — no extra text or reasoning.
        2. Describe characters consistently across ALL scenes: age, build, hair, clothing, expression, posture.
        3. DO NOT change the character’s physical description or outfit between scenes — consistency is essential.
        4. DO NOT use character names — use descriptive phrases like "slim young adult woman with shoulder-length brown hair".
        5. Include artistic style, composition, lighting, and relevant keywords.
        6. Ensure clear character positioning, interaction, and prominence.
        7. Environmental elements must support, not overshadow, the characters.
"""

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
