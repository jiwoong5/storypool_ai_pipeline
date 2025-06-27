from object_analyst.object_analyst_interface import ObjectAnalysisInterface
from llama_tools.llama_helper import LlamaHelper
from api_caller.api_caller_selector import APICallerSelector


class LlamaObjectAnalyst(ObjectAnalysisInterface):
    def __init__(self, model_name: str = "llama3.2:3b", api_url: str = "http://localhost:11434/api/generate"):
        self.llm_helper = LlamaHelper(
            call_api_fn=APICallerSelector.select("llama", model=model_name, api_url=api_url),
            delimiter="2969"
        )
        self.instruction_guide = "Extract main characters or a main character in the following prompts."
        self.caution = "Caution: Must add delimiters '2969' at the beginning and end of list of main characters or main character."

    def extract_objects(self, scenes: str) -> str:
        is_valid_prompt = bool(scenes and scenes.strip())
        if not is_valid_prompt:
            return f"내용 없음"

        instruction = self.llm_helper.build_instruction(self.instruction_guide, scenes.strip(), self.caution)
        return self.llm_helper.retry_and_extract(instruction, description=f"Scenes 에서 등장인물 추출")
