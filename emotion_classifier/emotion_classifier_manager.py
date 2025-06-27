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

    def process(self, input_path: str, output_path: str):
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"Input file not found: {input_path}")

        with open(input_path, 'r', encoding='utf-8') as f:
            text = f.read().strip()

        if not text:
            raise ValueError("Input text is empty")

        scenes = self.parse_scenes(text)
        results = []

        for scene_title, scene_text in scenes.items():
            result = self.classifier.classify_emotion_with_score(scene_text)
            result_line = f"{scene_title} => {result['emotion']} (score: {result['score']:.2f})"
            results.append(result_line)

        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("\n".join(results))

        return results