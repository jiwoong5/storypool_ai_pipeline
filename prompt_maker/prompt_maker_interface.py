from abc import ABC, abstractmethod

class PromptMakerInterface(ABC):
    @abstractmethod
    def make_prompt(self, scene: str, scene_index: int) -> str:
        pass
