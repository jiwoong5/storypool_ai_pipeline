from typing import Dict, Any
import os
from story_writer.story_writer_selector import StoryWriterSelector
from story_writer.story_writer_interface import StoryWriterInterface

class StoryWriterManager:
    def __init__(self, story_writer_interface: StoryWriterInterface):
        self.writer = story_writer_interface

    def process(self, input_text: str) -> str:
        """
        Generate story directly from input text.
        """
        return self.writer.generate_story(input_text)

    def process_from_path(self, input_path: str, output_path: str) -> str:
        """
        Read text from input file, generate story, and write to output file.
        """
        with open(input_path, 'r', encoding='utf-8') as f:
            text_content = f.read()

        result = self.process(text_content)

        if output_path:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(result)

        return result
