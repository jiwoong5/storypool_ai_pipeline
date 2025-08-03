import os
import re
from typing import Optional, Dict
from emotion_classifier.emotion_classifier_interface import EmotionClassifierInterface

class EmotionClassifierManager:
    def __init__(self, classifier: EmotionClassifierInterface):
        self.classifier = classifier

    def parse_scenes(self, text: str) -> Dict[str, str]:
        # Scene 구간별로 나눔
        pattern = r"(Scene \d+:)"
        parts = re.split(pattern, text)
        scenes = {}
        for i in range(1, len(parts), 2):
            scene_title = parts[i].strip()
            scene_content = parts[i + 1].strip() if i + 1 < len(parts) else ""
            scenes[scene_title] = scene_content
        return scenes

    def process(self, input_text:str):
        return self.classifier.classify_emotion_with_score(input_text)