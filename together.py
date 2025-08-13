import os
import json
from pathlib import Path

BASE_DIR = Path(".")  # 현재 디렉토리 기준
STORIES_DIR = BASE_DIR / "storys"
SCENES_DIR = BASE_DIR / "scenes"
PROMPTS_DIR = BASE_DIR / "prompts"
RESULTS_DIR = BASE_DIR / "results"

RESULTS_DIR.mkdir(exist_ok=True)

def merge_story_files():
    # storys 디렉토리의 모든 txt 파일
    story_files = list(STORIES_DIR.glob("*.txt"))
    
    if not story_files:
        print("No story files found in ./storys/")
        return
    
    for story_file in story_files:
        story_name = story_file.stem
        print(f"Processing {story_name}...")

        # 1. story 텍스트
        with open(story_file, 'r', encoding='utf-8') as f:
            story_text = f.read().strip()
        
        # 2. scenes JSON
        scenes_file = SCENES_DIR / f"{story_name}_scenes.json"
        if not scenes_file.exists():
            print(f"Warning: Scenes file not found for {story_name}, skipping...")
            continue
        with open(scenes_file, 'r', encoding='utf-8') as f:
            scenes_data = json.load(f)
        
        # 3. prompts JSON
        prompts_file = PROMPTS_DIR / f"{story_name}_prompt.txt"
        if not prompts_file.exists():
            print(f"Warning: Prompts file not found for {story_name}, skipping...")
            continue
        with open(prompts_file, 'r', encoding='utf-8') as f:
            try:
                prompts_data = json.load(f)
            except json.JSONDecodeError:
                # 만약 리스트 형태가 아니라 그냥 문자열이면 그대로 저장
                prompts_text = f.read()
                prompts_data = [{"generated_prompt": prompts_text}]
        
        # 4. 합치기
        merged_result = {
            "story_name": story_name,
            "story_text": story_text,
            "scenes": scenes_data.get("scenes", []),
            "prompts": prompts_data
        }
        
        # 5. 결과 파일 저장
        result_file = RESULTS_DIR / f"{story_name}_results.json"
        with open(result_file, 'w', encoding='utf-8') as f:
            json.dump(merged_result, f, ensure_ascii=False, indent=2)
        
        print(f"Saved merged result: {result_file}")

if __name__ == "__main__":
    merge_story_files()
