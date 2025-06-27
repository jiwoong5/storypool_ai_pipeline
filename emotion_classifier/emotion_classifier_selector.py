from emotion_classifier.emotion_classifier_interface import EmotionClassifierInterface
from emotion_classifier.minilm_classifier import MiniLMClassifier

class EmotionClassifierSelector:
    @staticmethod
    def get_emotion_classifier(classifier_type: str = 'minilm', **kwargs) -> EmotionClassifierInterface:
        if classifier_type == 'minilm':
            return MiniLMClassifier(**kwargs)
        # 다른 분류기 추가 가능 (예: 'bert', 'roberta')
        raise ValueError(f"Unsupported classifier type: {classifier_type}")