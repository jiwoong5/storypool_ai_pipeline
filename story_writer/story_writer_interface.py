from abc import ABC, abstractmethod

class StoryWriterInterface(ABC):
    @abstractmethod
    def generate_story(self, text_content: str) -> str:
        pass