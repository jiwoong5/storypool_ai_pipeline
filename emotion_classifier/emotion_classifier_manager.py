import os
import re
from typing import Optional, Dict
from emotion_classifier.emotion_classifier_interface import EmotionClassifierInterface

class EmotionClassifierManager:
    def __init__(self, classifier: EmotionClassifierInterface):
        self.classifier = classifier

    def process(self, input_text:str):
        return self.classifier.classify_emotion_with_score(input_text)