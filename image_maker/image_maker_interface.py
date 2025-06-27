# image_maker_interface.py
from abc import ABC, abstractmethod

class ImageMakerInterface(ABC):
    @abstractmethod
    def generate_image(self, prompts: list[str], output_dir: str):
        pass