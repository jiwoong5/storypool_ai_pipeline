from abc import ABC, abstractmethod

class OCRInterface(ABC):
    @abstractmethod
    def read_text(self, image_path: str, lang_list: list) -> list:
        pass