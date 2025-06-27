from story_writer.story_writer_interface import StoryWriterInterface
from llama_tools.llama_helper import LlamaHelper
from api_caller.api_caller_selector import APICallerSelector

class LlamaStoryWriter(StoryWriterInterface):
    def __init__(self, model: str = "llama3.2:3b", api_url: str = "http://localhost:11434/api/generate"):
        self.llm_helper = LlamaHelper(
            call_api_fn=APICallerSelector.select("llama", model=model, api_url=api_url),
            delimiter="---"
        )

    def generate_story(self, text_content: str) -> str:
        main_instruction = "Read the text and create a story based on it."
        caution = "The story must follow the characters and their descriptions. And Must add delimiters '---' at the beginning and end of the story."
        instruction = self.llm_helper.build_instruction(main_instruction, text_content, caution)
        return self.llm_helper.retry_and_extract(instruction, description="이야기 생성")
