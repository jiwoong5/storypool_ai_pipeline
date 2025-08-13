import os
import json
from pathlib import Path

from scene_parser.scene_parser_selector import SceneParserSelector
from scene_parser.scene_parser_manager import SceneParserManager
from prompt_maker.prompt_maker_selector import PromptMakerSelector
from prompt_maker.prompt_maker_manager import PromptMakerManager


class StoryProcessor:
    def __init__(self, base_dir="."):
        """
        스토리 처리기 초기화
        
        Args:
            base_dir (str): 베이스 디렉토리 경로
        """
        self.base_dir = Path(base_dir)
        self.stories_dir = self.base_dir / "storys"
        self.scenes_dir = self.base_dir / "scenes"
        self.prompts_dir = self.base_dir / "prompts"
        
        # 출력 디렉토리 생성
        self.scenes_dir.mkdir(exist_ok=True)
        self.prompts_dir.mkdir(exist_ok=True)
        
        # 프로세서 초기화
        self.scene_parser = self._init_scene_parser()
        self.prompt_maker = self._init_prompt_maker()
    
    def _init_scene_parser(self):
        """Scene Parser 초기화"""
        parser = SceneParserSelector.get_parser(parser_type="llama")
        return SceneParserManager(parser)
    
    def _init_prompt_maker(self):
        """Prompt Maker 초기화"""
        prompt_maker = PromptMakerSelector.get_prompt_maker("llama")
        return PromptMakerManager(prompt_maker)
    
    def load_story(self, story_name):
        """
        스토리 파일 로드
        
        Args:
            story_name (str): 스토리 파일명 (확장자 제외)
            
        Returns:
            str: 스토리 내용
        """
        story_path = self.stories_dir / f"{story_name}.txt"
        
        if not story_path.exists():
            raise FileNotFoundError(f"Story file not found: {story_path}")
        
        with open(story_path, 'r', encoding='utf-8') as f:
            return f.read().strip()
    
    def save_scenes(self, story_name, scenes_data):
        """
        Scene parsing 결과를 파싱하지 않고 그대로 저장
        (여러 scene이 있을 경우에도 전체를 하나의 파일로 저장)
        """
        try:
            # 문자열이면 그대로, dict/list면 JSON 문자열로 변환
            if isinstance(scenes_data, (dict, list)):
                scene_str = json.dumps(scenes_data, ensure_ascii=False, indent=2)
            else:
                scene_str = str(scenes_data)

            # story 전체 scenes 파일명
            scene_filename = f"{story_name}_scenes.json"
            scene_path = self.scenes_dir / scene_filename

            with open(scene_path, "w", encoding="utf-8") as f:
                f.write(scene_str)

            print(f"Saved all scenes to: {scene_path}")

        except Exception as e:
            print(f"Error saving scenes for {story_name}: {e}")
    
    def save_prompts(self, story_name, scenes_data):
        """
        scenes_data 전체를 하나의 prompt로 생성하고 저장
        (JSON 파싱 없이 그대로 사용)
        """
        try:
            # 문자열이면 그대로, dict/list면 JSON 문자열로 변환
            if isinstance(scenes_data, (dict, list)):
                scene_str = json.dumps(scenes_data, ensure_ascii=False, indent=2)
            else:
                scene_str = str(scenes_data)

            # prompt 생성
            prompt_result = self.prompt_maker.process(scene_str)

            # prompt_result가 dict이면 텍스트 추출, 아니면 문자열 그대로
            if isinstance(prompt_result, dict):
                prompt_text = (
                    prompt_result.get("prompt") or
                    prompt_result.get("text") or
                    prompt_result.get("content") or
                    json.dumps(prompt_result, ensure_ascii=False, indent=2)
                )
            else:
                prompt_text = str(prompt_result)

            # 전체 scenes에 대한 단일 prompt 파일로 저장
            prompt_filename = f"{story_name}_prompt.txt"
            prompt_path = self.prompts_dir / prompt_filename

            with open(prompt_path, 'w', encoding='utf-8') as f:
                f.write(prompt_text)

            print(f"Saved prompt for all scenes: {prompt_path}")

        except Exception as e:
            print(f"Error generating prompt for {story_name}: {e}")
    
    def load_existing_scenes(self, story_name):
        """
        기존에 저장된 전체 scenes 파일을 로드하여 단일 프롬프트 생성
        (scene parsing은 이미 완료된 상태에서 프롬프트만 생성)
        
        Args:
            story_name (str): 스토리 이름
            
        Returns:
            int: 생성된 프롬프트 파일 수 (항상 1)
        """
        # story 전체 scenes 파일
        scene_file = self.scenes_dir / f"{story_name}_scenes.json"
        
        if not scene_file.exists():
            print(f"No scene file found for story: {story_name}")
            return 0
        
        try:
            with open(scene_file, 'r', encoding='utf-8') as f:
                scenes_data = f.read()  # 그대로 문자열로 읽기
            
            # prompt 생성
            prompt_result = self.prompt_maker.process(scenes_data)
            print("DEBUG prompt_result:", prompt_result)

            # prompt_result가 dict이면 텍스트 추출, 아니면 문자열 그대로
            if isinstance(prompt_result, dict):
                prompt_text = (
                    prompt_result.get("prompt") or
                    prompt_result.get("text") or
                    prompt_result.get("content") or
                    json.dumps(prompt_result, ensure_ascii=False, indent=2)
                )
            else:
                prompt_text = str(prompt_result)
            
            # 단일 prompt 파일 저장
            prompt_filename = f"{story_name}_prompt.txt"
            prompt_path = self.prompts_dir / prompt_filename
            with open(prompt_path, 'w', encoding='utf-8') as f:
                f.write(prompt_text)
            
            print(f"Generated prompt for all scenes: {prompt_path}")
            return 1  # 처리된 prompt 파일 수

        except Exception as e:
            print(f"Error generating prompt for {story_name}: {e}")
            return 0

    
    def process_story(self, story_name):
        """
        단일 스토리 처리
        
        Args:
            story_name (str): 처리할 스토리 이름
        """
        try:
            print(f"Processing story: {story_name}")
            
            # 1. 스토리 로드
            story_content = self.load_story(story_name)
            print(f"Loaded story content: {len(story_content)} characters")
            
            # 2. Scene parsing
            print("Running scene parsing...")
            scenes_result = self.scene_parser.process(story_content)
            
            # 3. Scene 결과 저장
            print("Saving scenes...")
            self.save_scenes(story_name, scenes_result)
            
            # 4. 각 Scene에 대해 개별 Prompt 생성 및 저장
            print("Generating and saving prompts for each scene...")
            self.save_prompts(story_name, scenes_result)
            
            print(f"Successfully processed story: {story_name}\n")
            
        except Exception as e:
            print(f"Error processing story {story_name}: {e}")
    
    def generate_prompts_only(self, story_name=None):
        """
        이미 존재하는 scene 파일들에 대해서만 프롬프트 생성
        (scene parsing은 건너뛰고 프롬프트만 생성)
        
        Args:
            story_name (str, optional): 특정 스토리만 처리. None이면 모든 스토리 처리
        """
        if story_name:
            # 특정 스토리만 처리
            count = self.load_existing_scenes(story_name)
            print(f"Generated {count} prompts for story: {story_name}")
        else:
            # 모든 스토리 처리
            story_names = set()
            for scene_file in self.scenes_dir.glob("*_scene*.json"):
                story_name = scene_file.stem.split('_scene')[0]
                story_names.add(story_name)
            
            total_count = 0
            for story_name in story_names:
                count = self.load_existing_scenes(story_name)
                total_count += count
            
            print(f"Generated {total_count} prompts for {len(story_names)} stories")
    
    def process_all_stories(self):
        """
        ./storys/ 디렉토리의 모든 스토리 파일 처리
        """
        if not self.stories_dir.exists():
            print(f"Stories directory not found: {self.stories_dir}")
            return
        
        # .txt 파일 찾기
        story_files = list(self.stories_dir.glob("*.txt"))
        
        if not story_files:
            print(f"No story files found in {self.stories_dir}")
            return
        
        print(f"Found {len(story_files)} story files")
        
        for story_file in story_files:
            story_name = story_file.stem  # 확장자 제거한 파일명
            self.process_story(story_name)
    
    def get_story_list(self):
        """
        사용 가능한 스토리 목록 반환
        
        Returns:
            list: 스토리 파일명 리스트 (확장자 제외)
        """
        if not self.stories_dir.exists():
            return []
        
        story_files = list(self.stories_dir.glob("*.txt"))
        return [f.stem for f in story_files]


def main():
    """메인 실행 함수"""
    processor = StoryProcessor()
    
    # 사용 가능한 스토리 목록 확인
    story_list = processor.get_story_list()
    
    if not story_list:
        print("No story files found in ./storys/ directory")
        print("Please add story files (story1.txt, story2.txt, etc.) to the ./storys/ directory")
        return
    
    print(f"Available stories: {story_list}")
    
    # 모든 스토리 처리
    processor.process_all_stories()
    
    print("All stories processed successfully!")


if __name__ == "__main__":
    main()