from story_writer.story_writer_interface import StoryWriterInterface
from llama_tools.llama_helper import LlamaHelper
from api_caller.api_caller_selector import APICallerSelector
import os

class LlamaStoryWriter(StoryWriterInterface):
    def __init__(self, model_name: str = "llama3.2:3b", api_url: str = None):
        from dotenv import load_dotenv
        load_dotenv()
        host = api_url or os.getenv("OLLAMA_HOST", "http://localhost:11434")
        self.api_url = host.rstrip("/") + "/api/generate"
        self.model_name = model_name
        self.llm_helper = LlamaHelper(
            call_api_fn=APICallerSelector.select("llama", model=model_name, api_url=self.api_url)
        )

    def generate_story(self, text_content: str) -> str:
        main_instruction = "Read the text and create a story based on it."
        caution = "The story must follow the characters and their descriptions."
        instruction = self.llm_helper.build_instruction(main_instruction, text_content, caution)
        return self.llm_helper.retry_and_extract(instruction, description="이야기 생성")
