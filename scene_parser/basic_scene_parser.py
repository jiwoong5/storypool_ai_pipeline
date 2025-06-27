from scene_parser.scene_parser_interface import SceneParserInterface

class BasicSceneParser(SceneParserInterface):
    def __init__(self):
        self.keywords = ["One day", "Then one day", "However", "Then", "At that moment", "And", "Eventually"]

    def parse(self, text: str) -> dict[int, str]:
        paragraphs = self.split_into_paragraphs(text)
        scenes = self.split_by_keywords(paragraphs)
        return self.label_scenes(scenes)

    def split_into_paragraphs(self, text: str) -> list[str]:
        paragraphs = text.split("\n\n")
        return [p.strip() for p in paragraphs if p.strip()]

    def split_by_keywords(self, paragraphs: list[str]) -> list[str]:
        result = []
        for paragraph in paragraphs:
            temp = paragraph
            for keyword in self.keywords:
                if keyword in temp:
                    parts = temp.split(keyword)
                    for i, part in enumerate(parts):
                        if part.strip():
                            if i != 0:
                                result.append(keyword + part.strip())
                            else:
                                result.append(part.strip())
                    break
            else:
                result.append(temp)
        return result

    def label_scenes(self, scenes: list[str]) -> dict[int, str]:
        labeled_scenes = {}
        for i, scene in enumerate(scenes, start=1):
            labeled_scenes[i] = scene.strip()  # scene_number: scene_text
        return labeled_scenes