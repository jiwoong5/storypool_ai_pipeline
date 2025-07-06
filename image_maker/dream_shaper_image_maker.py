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
        with torch.no_grad():
            image = self.pipe(
                prompt,
                negative_prompt="low quality, blurry",
                num_inference_steps=25
            ).images[0]
        return image
