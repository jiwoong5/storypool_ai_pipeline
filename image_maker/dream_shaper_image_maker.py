import torch
from diffusers import StableDiffusionPipeline
from PIL import Image
from image_maker.image_maker_interface import ImageMakerInterface


class DreamShaperImageMaker(ImageMakerInterface):
    def __init__(self, model_name='Lykon/dreamshaper-8'):
        # 디바이스 설정
        self.device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")

        # DreamShaper 모델 로드
        self.pipe = StableDiffusionPipeline.from_pretrained(model_name, torch_dtype=torch.float16)
        self.pipe = self.pipe.to(self.device)

    def generate_image(self, prompt: str) -> Image.Image:
        with torch.no_grad():
            # 이미지 생성 (안전 모드 비활성화)
            image = self.pipe(
                prompt,
                negative_prompt="low quality, blurry",
                num_inference_steps=25
            ).images[0]

        return image
