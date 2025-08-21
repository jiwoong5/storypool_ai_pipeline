import os
from pathlib import Path
from image_maker.image_maker_selector import ImageMakerSelector
from image_maker.image_maker_manager import ImageMakerManager  # 기존 코드 기준

def generate_images_from_prompts(prompt_file_path: str, output_dir: str):
    # 1. 프롬프트 파일 읽기
    with open(prompt_file_path, 'r', encoding='utf-8') as f:
        prompts = f.readlines()
    
    # 이미지 저장 폴더 만들기
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # ImageMaker 준비
    image_maker = ImageMakerSelector.get_image_maker('sdxl')
    manager = ImageMakerManager(image_maker)
    
    for idx, prompt in enumerate(prompts, start=1):
        prompt = prompt.strip()
        if not prompt:
            continue
        
        # 2. 이미지 생성
        images = manager.process(prompt)  # List[bytes]
        
        # 3. 장면별로 저장 (png)
        for img_idx, img_bytes in enumerate(images, start=1):
            file_path = os.path.join(output_dir, f"story1_scene{idx}_{img_idx}.png")
            with open(file_path, 'wb') as f:
                f.write(img_bytes)
        
        print(f"Scene {idx} generated: {len(images)} images saved.")

    print("All images generated successfully.")

if __name__ == "__main__":
    # 사용 예시
    generate_images_from_prompts(
        prompt_file_path='./prompts/story1_prompt.txt',
        output_dir='./images'
    )
