import re
from pathlib import Path
from image_maker.image_maker_interface import ImageMakerInterface

class ImageMakerManager:
    def __init__(self, image_maker: ImageMakerInterface):
        self.image_maker = image_maker

    def extract_prompts(self, filename: str) -> list[str]:
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()

        scene_blocks = re.split(r'Scene \d+:', content)
        prompts = [block.strip() for block in scene_blocks if block.strip()]
        return prompts

    def process(self, input_path: str, output_dir: str):
        prompts = self.extract_prompts(input_path)
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        for i, prompt in enumerate(prompts, 1):
            try:
                print(f"\n[{i}/{len(prompts)}] Generating image for prompt: {prompt[:60]}...")
                image = self.image_maker.generate_image(prompt)
                image.save(output_dir / f"result{i}.png")
                print(f"Saved to: result{i}.png")
            except Exception as e:
                print(f"Error in prompt {i}: {e}")
