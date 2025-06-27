from sentence_transformers import SentenceTransformer, util
import torch
from typing import List, Dict
from emotion_classifier.emotion_classifier_interface import EmotionClassifierInterface

class MiniLMClassifier(EmotionClassifierInterface):
    def __init__(self, emotion_words: List[str] = None):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.emotion_words = emotion_words or [
            'happiness', 'sadness', 'anger',
            'fear', 'disgust', 'surprise',
            'anticipation', 'trust'
        ]
        self.emotion_embeddings = self.model.encode(self.emotion_words, convert_to_tensor=True)

    def classify_emotion(self, text: str) -> str:
        scores = self._calculate_scores(text)
        return self.emotion_words[scores.argmax()]

    def classify_emotion_with_score(self, text: str) -> Dict[str, float]:
        scores = self._calculate_scores(text)
        max_idx = scores.argmax()
        return {
            "emotion": self.emotion_words[max_idx],
            "score": scores[max_idx].item()
        }

    def _calculate_scores(self, text: str) -> torch.Tensor:
        text_embedding = self.model.encode([text], convert_to_tensor=True)
        return util.cos_sim(text_embedding, self.emotion_embeddings)[0]