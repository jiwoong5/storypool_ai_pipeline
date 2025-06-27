from image_maker.image_maker_selector import ImageMakerSelector
from image_maker.image_maker_manager import ImageMakerManager

if __name__ == "__main__":
    image_maker = ImageMakerSelector.get_image_maker('dream_shaper')

    manager = ImageMakerManager(image_maker)

    generated_image = manager.process("image_maker/input.txt", "image_maker/")

    print("이미지 생성 완료! ./image_maker/ 에 저장되었습니다.")

