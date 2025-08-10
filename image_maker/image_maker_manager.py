from typing import List
from image_maker.image_maker_interface import ImageMakerInterface
from PIL import Image
import json, os, io

class ImageMakerManager:
    def __init__(self, image_maker: ImageMakerInterface):
        self.image_maker = image_maker

    @staticmethod
    def image_to_bytes(image: Image.Image, format: str = "PNG") -> bytes:
        with io.BytesIO() as output:
            image.save(output, format=format)
            return output.getvalue()

    def process(self, prompts: str) -> List[bytes]:
        """
        Generate images from a list of prompt strings and return as byte data.

        Args:
            prompts: A JSON-serialized list of dicts, each with a 'generated_prompt' field.

        Returns:
            List of image bytes (e.g., PNG format).
        """
        results = []

        if not isinstance(prompts, str):
            raise TypeError(f"Expected prompts to be str, got {type(prompts)}")

        # 2) JSON 파싱 시도
        try:
            parsed_prompts = json.loads(prompts)
        except json.JSONDecodeError as e:
            print("JSONDecodeError:", e)
            raise

        # 3) 'generated_prompt' 키 존재 및 값 타입 점검
        extracted_prompts = []
        for i, item in enumerate(parsed_prompts, 1):
            if not isinstance(item, dict):
                raise TypeError(f"Item {i} is not a dict: {item}")
            if 'generated_prompt' not in item:
                raise KeyError(f"Item {i} missing 'generated_prompt' key")
            prompt_value = item['generated_prompt']
            if not isinstance(prompt_value, str):
                raise TypeError(f"Item {i} 'generated_prompt' is not a string: {prompt_value}")
            extracted_prompts.append(prompt_value)

        # 4) 이미지 생성 루프
        for i, prompt in enumerate(extracted_prompts, 1):
            try:
                image = self.image_maker.generate_image(prompt)
                image_bytes = self.image_to_bytes(image)
                results.append(image_bytes)
            except Exception as e:
                print(f"Error in prompt {i}: {e}")
                results.append(None)

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
        