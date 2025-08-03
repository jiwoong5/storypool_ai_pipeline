from emotion_classifier.emotion_classifier_manager import EmotionClassifierManager
from emotion_classifier.emotion_classifier_selector import EmotionClassifierSelector

if __name__ == "__main__":
    classifer = EmotionClassifierSelector.get_emotion_classifier("minilm")
    manager = EmotionClassifierManager(classifer)
    print(manager.process("misterious"))
