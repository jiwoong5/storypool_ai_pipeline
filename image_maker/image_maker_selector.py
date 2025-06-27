from image_maker.dream_shaper_image_maker import DreamShaperImageMaker
from image_maker.ghibli_diffusion_image_maker import GhibliDiffusionImageMaker
from image_maker.image_maker_interface import ImageMakerInterface

class ImageMakerSelector:
    @staticmethod
    def get_image_maker(model_name: str = "dream_shaper") -> ImageMakerInterface:
        if model_name == "ghibli_diffusion":
            return GhibliDiffusionImageMaker()
        if model_name == "dream_shaper":
            return DreamShaperImageMaker()
        else:
            raise ValueError(f"지원하지 않는 이미지 생성기: {model_name}")
