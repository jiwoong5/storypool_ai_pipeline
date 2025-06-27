from abc import ABC, abstractmethod
from typing import Dict

class EmotionClassifierInterface(ABC):
    @abstractmethod
    def classify_emotion(self, text: str) -> str:
        pass

    @abstractmethod
    def classify_emotion_with_score(self, text: str) -> Dict[str, float]:
        pass