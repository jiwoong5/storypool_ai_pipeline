import torch
from diffusers import StableDiffusionPipeline
from PIL import Image
from image_maker.image_maker_interface import ImageMakerInterface


class DreamShaperImageMaker(ImageMakerInterface):
    def __init__(self, model_name='Lykon/dreamshaper-8'):
        # 디바이스 설정
        if torch.cuda.is_available():
            self.device = torch.device("cuda")
            dtype = torch.float16
        elif torch.backends.mps.is_available():
            self.device = torch.device("mps")
            dtype = torch.float32
        else:
            self.device = torch.device("cpu")
            dtype = torch.float32

        # DreamShaper 모델 로드
        self.pipe = StableDiffusionPipeline.from_pretrained(model_name, torch_dtype=dtype)
        self.pipe = self.pipe.to(self.device)

    def generate_image(self, prompt: str) -> Image.Image:
        max_attempts = 3
        attempt = 0

        while attempt < max_attempts:
            with torch.no_grad():
                result = self.pipe(
                    prompt,
                    negative_prompt="low quality, blurry",
                    num_inference_steps=25
                )
                image = result.images[0]

                # NSFW 체크 (diffusers의 safety_checker가 결과에 NSFW 판단 여부 포함)
                if hasattr(result, 'nsfw_content_detected'):
                    nsfw_detected = result.nsfw_content_detected[0]
                else:
                    nsfw_detected = False  # safety_checker 없으면 false로 간주

                if nsfw_detected:
                    print(f"NSFW content detected on attempt {attempt + 1}, regenerating...")
                    attempt += 1
                else:
                    return image

        print("Max NSFW retries reached, returning last generated image.")
        return image
