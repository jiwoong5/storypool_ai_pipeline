import torch
from diffusers import StableDiffusionXLPipeline
from PIL import Image
from image_maker.image_maker_interface import ImageMakerInterface


class SDXLImageMaker(ImageMakerInterface):
    def __init__(self, model_name='stabilityai/stable-diffusion-xl-base-1.0'):
        # 디바이스 설정
        if torch.cuda.is_available():
            self.device = torch.device("cuda")
            dtype = torch.float16  # SDXL은 float16 권장
        elif torch.backends.mps.is_available():
            self.device = torch.device("mps")
            dtype = torch.float32
        else:
            self.device = torch.device("cpu")
            dtype = torch.float32

        # SDXL Standard 모델 로드
        self.pipe = StableDiffusionXLPipeline.from_pretrained(model_name, torch_dtype=dtype)
        self.pipe = self.pipe.to(self.device)

    def generate_image(self, prompt: str) -> Image.Image:
        max_attempts = 3
        attempt = 0

        while attempt < max_attempts:
            with torch.no_grad():
                result = self.pipe(
                    prompt,
                    negative_prompt="low quality, blurry, NSFW",
                    height=768,
                    width=768,
                    num_inference_steps=25
                )
                image = result.images[0]

                # NSFW 체크
                if hasattr(result, 'nsfw_content_detected'):
                    nsfw_detected = result.nsfw_content_detected[0]
                else:
                    nsfw_detected = False

                if nsfw_detected:
                    print(f"NSFW content detected on attempt {attempt + 1}, regenerating...")
                    attempt += 1
                else:
                    return image

        print("Max NSFW retries reached, returning last generated image.")
        return image
