from abc import ABC, abstractmethod

class ObjectAnalysisInterface(ABC):
    @abstractmethod
    def extract_objects(self, scenes: str) -> str:
        pass
