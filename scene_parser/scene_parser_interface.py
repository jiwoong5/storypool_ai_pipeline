from abc import ABC, abstractmethod

class SceneParserInterface(ABC):
    @abstractmethod
    def parse(self, text: str) -> list[str]:
        pass
