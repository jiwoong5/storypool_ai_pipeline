from prompt_maker.prompt_maker_interface import PromptMakerInterface
from llama_tools.llama_helper import LlamaHelper
from api_caller.api_caller_selector import APICallerSelector


class LlamaPromptMaker(PromptMakerInterface):
    def __init__(self, model_name: str = "llama3.2:3b", api_url: str = "http://localhost:11434/api/generate"):
        self.llm_helper = LlamaHelper(
            call_api_fn=APICallerSelector.select("llama", model=model_name, api_url=api_url),
            delimiter="2969"
        )
        self.main_instruction = "Transform this scene into an image generation prompt in the style of a fairy-tale illustration. if possible, include the main character and some description of them.:"
        self.caution = "Must add delimiters '2969' at the beginning and end of the prompt."

    def make_prompt(self, scene: str, scene_index: int) -> str:
        is_valid_scene = bool(scene and scene.strip())
        if not is_valid_scene:
            return f"Scene {scene_index} 내용 없음"

        instruction = self.llm_helper.build_instruction(self.main_instruction, scene.strip(), self.caution)
        return self.llm_helper.retry_and_extract(instruction, description=f"Scene {scene_index} 프롬프트 생성")