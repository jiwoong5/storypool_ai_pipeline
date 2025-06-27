class SceneParserManager:
    def __init__(self, parser):
        self.parser = parser

    def load_text(self, filename: str) -> str:
        with open(filename, "r", encoding="utf-8") as f:
            return f.read()

    def save_scenes(self, scenes: dict[int, str], output_file: str):
        with open(output_file, "w") as f:
            for scene_num, scene_text in scenes.items():
                f.write(f"Scene {scene_num}: {scene_text}\n\n")

    def process(self, input_file: str, output_file: str):
        text = self.load_text(input_file)
        scenes = self.parser.parse(text)
        self.save_scenes(scenes, output_file)
        return scenes