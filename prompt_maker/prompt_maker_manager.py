import re
from prompt_maker.prompt_maker_interface import PromptMakerInterface

class PromptMakerManager:
    def __init__(self, prompt_maker: PromptMakerInterface):
        self.prompt_maker = prompt_maker

    def load_text(self, filename: str) -> str:
        with open(filename, "r", encoding="utf-8") as f:
            return f.read()

    def split_scenes(self, text: str) -> list[str]:
        # "Scene N:" 패턴 찾기
        pattern = r'(Scene \d+:)'
        matches = list(re.finditer(pattern, text))

        scenes = []
        for i in range(len(matches)):
            start = matches[i].end()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
            scene_text = text[start:end].strip()
            scenes.append(scene_text)

        return scenes

    def generate_prompts(self, scenes: list[str]) -> list[str]:
        prompts = []
        for idx, scene in enumerate(scenes, start=1):
            prompt = self.prompt_maker.make_prompt(scene, idx)
            prompts.append(prompt)
            print(f"Scene {idx} 처리 완료")
        return prompts

    def save_prompts(self, prompts: list[str], filename: str):
        with open(filename, "w", encoding="utf-8") as f:
            for idx, prompt in enumerate(prompts, start=1):
                f.write(f"Scene {idx}:\n")
                f.write(prompt.strip())
                f.write("\n\n")  # 씬끼리 간격 두기
        print(f"모든 scene 프롬프트 생성 완료 → {filename} 저장됨")


    def process(self, input_path: str, output_path: str):
        text = self.load_text(input_path)

        scenes = self.split_scenes(text)

        prompts = []
        for idx, scene in enumerate(scenes, start=1):
            prompt = self.prompt_maker.make_prompt(scene, idx)
            prompts.append(prompt)

        self.save_prompts(prompts, output_path)
        return prompts