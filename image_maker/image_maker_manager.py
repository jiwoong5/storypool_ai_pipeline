from typing import List
from image_maker.image_maker_interface import ImageMakerInterface
from PIL import Image

class ImageMakerManager:
    def __init__(self, image_maker: ImageMakerInterface):
        self.image_maker = image_maker

    def process(self, prompts: List[str]) -> List[Image.Image]:
        """
        Generate images from a list of prompt strings.

        Returns:
            List of PIL Image objects.
        """
        results = []

        for i, prompt in enumerate(prompts, 1):
            try:
                print(f"\n[{i}/{len(prompts)}] Generating image for prompt: {prompt[:60]}...")
                image = self.image_maker.generate_image(prompt)
                results.append(image)
            except Exception as e:
                print(f"Error in prompt {i}: {e}")
                results.append(None)  # Or skip, depending on your needs

        return results