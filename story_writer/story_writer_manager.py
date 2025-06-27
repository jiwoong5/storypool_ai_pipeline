from typing import Dict, Any
import os
from story_writer.story_writer_selector import StoryWriterSelector
from story_writer.story_writer_interface import StoryWriterInterface

class StoryWriterManager:
    def __init__(self, story_writer_interface: StoryWriterInterface):
        self.writer = story_writer_interface

    def process(self, input_path: str, output_path: str) -> Dict[str, Any]:
        with open(input_path, 'r', encoding='utf-8') as f:
            text_content = f.read()

        result = self.writer.generate_story(text_content)

        if output_path:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(result)
        return result