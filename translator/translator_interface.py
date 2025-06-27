from abc import ABC, abstractmethod

class TranslatorInterface(ABC):
    @abstractmethod
    def translate_text(self, text: str) -> str:
        pass

