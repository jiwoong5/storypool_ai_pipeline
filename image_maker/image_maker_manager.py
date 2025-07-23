from typing import List
from image_maker.image_maker_interface import ImageMakerInterface
from PIL import Image
import json, os

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
    
    def process_from_path(self, input_path: str, image_output_path: str) -> List[Image.Image]:
        """
        Read prompts from a JSON file and save generated images to the specified directory.

        Args:
            input_path (str): Path to a JSON file containing prompts.
            image_output_path (str): Directory to save generated images.
        
        Returns:
            List of generated PIL Image objects.
        """
        # Read prompts from JSON
        with open(input_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            items = data.get("prompts", [])
            prompt_pairs = [
                (item["scene_number"], item["generated_prompt"])
                for item in items if "generated_prompt" in item and "scene_number" in item
            ]

        # Ensure output directory exists
        os.makedirs(image_output_path, exist_ok=True)

        results = []

        for i, (scene_number, prompt) in enumerate(prompt_pairs, 1):
            print(f"\n[{i}/{len(prompt_pairs)}] Generating image for scene {scene_number}: {prompt[:60]}...")
            try:
                image = self.image_maker.generate_image(prompt)
                results.append(image)

                # Save image
                image_path = os.path.join(image_output_path, f"scene_{scene_number:03d}.png")
                image.save(image_path)
                print(f"Saved image to {image_path}")
            except Exception as e:
                print(f"Error in scene {scene_number}: {e}")
                results.append(None)

        return results
        