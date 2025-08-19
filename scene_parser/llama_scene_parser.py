import re, os, json
from typing import List, Dict, Any, Tuple
from api_responses.responses import SceneInfo, SceneParserResponse
from api_responses.responses import SceneParserResponse
from scene_parser.scene_parser_interface import SceneParserInterface
from llama_tools.llama_helper import LlamaHelper
from api_caller.api_caller_selector import APICallerSelector

class LlamaSceneParser(SceneParserInterface):
    """Llama 모델을 사용한 장면 파싱 클래스 (Location 추론 분리)"""
    
    def __init__(self, model_name: str = "llama3.2:3b", api_url: str = None):
        from dotenv import load_dotenv
        load_dotenv()
        host = api_url or os.getenv("OLLAMA_HOST", "http://localhost:11434")
        self.api_url = host.rstrip("/") + "/api/generate"
        self.model_name = model_name
        self.llm_helper = LlamaHelper(
            call_api_fn=APICallerSelector.select("llama", model=model_name, api_url=self.api_url),
        )
        self.llm_helper_location = LlamaHelper(
            call_api_fn=APICallerSelector.select("llama", model=model_name, api_url=self.api_url), temperature=0.5
        )

    def parse(self, text_content: str):
        """
        텍스트를 분석하여 장면별로 파싱하고 구조화된 결과를 반환
        
        Args:
            text_content (str): 분석할 텍스트 내용
            
        Returns:
            dict: 구조화된 장면 분석 결과 (JSON serializable)
        """
        try:
            # 1단계: 기본 장면 파싱 (location 제외)
            basic_scenes_data = self._parse_basic_scenes_with_correction(text_content)

            # 2단계: 장면별 location 추론
            locations = self._infer_locations(basic_scenes_data)

            # 3단계: location을 기본 장면 데이터에 추가
            enhanced_scenes_data = self._merge_locations(basic_scenes_data, locations)
            
            # 4단계: Dictionary로 반환
            return enhanced_scenes_data
            
        except Exception as e:
            print(f"장면 파싱 중 오류 발생: {e}")
            return {"error": f"장면 파싱 중 오류 발생: {str(e)}"}

    def _parse_basic_scenes(self, text_content: str):
        """
        기본 장면 파싱 (location 제외)
        """
        main_instruction = '''
        You are a professional story analyst. Carefully read the given text and divide the story into distinct scenes at sentences where logical transitions occur. Then, accurately extract the key elements of each scene. If a sentence is ambiguous about which scene it belongs to, you may attach it to either the preceding or following scene.

        Description of each field:

        1. scene_number: Indicates the sequential order of the scene within the story.

        2. characters: Lists all characters who appear in the scene, identified by name.

        3. time: Denotes the time when the scene occurs, such as morning, afternoon, evening, or a specific time.

        4. mood: Describes the emotional tone or atmosphere of the scene.

        5. story: The story field of each scene should contain the exact excerpt from the original text corresponding to that scene. The exact sentences from the original text corresponding to the scene. If the story fields of all scenes are concatenated in order, the complete story should be fully reconstructable.

        6. dialogue_count: The number of instances of dialogue present in the scene.

        
            Expected Output Format:
            {
                "scenes": [
                    {
                    "scene_number": "1",
                    "scene_title": "",
                    "characters": [],
                    "time": "",
                    "mood": "",
                    "story": "",
                    "dialogue_count": ""
                    },
                    {
                    "scene_number": "2",
                    "scene_title": "",
                    "characters": [],
                    "time": "",
                    "mood": "",
                    "story": "",
                    "dialogue_count": ""
                    }
                ],
                "total_scenes": "2",
                "main_characters": []
            }
        '''

        caution = '''
            Generate only the output in valid JSON format.
            '''
        
        instruction = self.llm_helper.build_instruction(main_instruction, text_content, caution)
        return self.llm_helper.retry_and_get_json(instruction, description="기본 장면 분석")

    def _find_missing_parts(self, original: str, reconstructed: str) -> List[List[str]]:
        """
        원본과 재구성된 텍스트를 비교하여 누락된 부분과 그 앞뒤 문장을 찾는다.
        original과 완전히 일치하지 않아도 루프가 안전하게 종료되도록 수정됨.
        
        Args:
            original (str): 원본 텍스트
            reconstructed (str): 재구성된 텍스트
            
        Returns:
            List[List[str]]: 각 누락 부분에 대해 [앞문장, 누락문장, 뒷문장] 형태의 리스트
        """
        basic_pattern = r'[.!?]+\s*'
        original_sentences = [s.strip() for s in re.split(basic_pattern, original) if s.strip()]
        reconstructed_sentences = [s.strip() for s in re.split(basic_pattern, reconstructed) if s.strip()]
        
        missing_parts = []
        orig_idx = 0
        recon_idx = 0
        
        while orig_idx < len(original_sentences):
            if recon_idx < len(reconstructed_sentences) and original_sentences[orig_idx] == reconstructed_sentences[recon_idx]:
                # 문장이 일치하면 다음으로 이동
                orig_idx += 1
                recon_idx += 1
            else:
                # 일치하지 않는 경우 누락 처리
                missing_sentence = original_sentences[orig_idx]
                prev_sentence = original_sentences[orig_idx - 1] if orig_idx > 0 else ""
                next_sentence = original_sentences[orig_idx + 1] if orig_idx + 1 < len(original_sentences) else ""
                
                missing_parts.append([prev_sentence, missing_sentence, next_sentence])
                orig_idx += 1  # recon_idx는 이동하지 않고 orig_idx만 증가시켜 무한 루프 방지
        
        return missing_parts

    def _find_target_scene_for_missing_part(self, missing_part: List[str], scenes: List[Dict]) -> int:
        """
        누락된 부분이 들어갈 적절한 scene을 찾는다
        
        Args:
            missing_part (List[str]): [앞문장, 누락문장, 뒷문장]
            scenes (List[Dict]): scene 데이터 리스트
            
        Returns:
            int: 대상 scene의 인덱스 (-1이면 찾지 못함)
        """
        prev_sentence, missing_sentence, next_sentence = missing_part
        
        # 앞문장과 뒷문장이 포함된 scene들을 찾기
        candidate_scenes = []
        
        for i, scene in enumerate(scenes):
            story = scene.get('story', '')
            score = 0
            
            # 앞문장이 포함되어 있는지 확인
            if prev_sentence and prev_sentence in story:
                score += 2
            
            # 뒷문장이 포함되어 있는지 확인
            if next_sentence and next_sentence in story:
                score += 2
            
            # 누락된 문장과 유사한 내용이 있는지 확인 (키워드 기반)
            missing_words = set(missing_sentence.lower().split())
            story_words = set(story.lower().split())
            common_words = missing_words.intersection(story_words)
            if len(common_words) > 0:
                score += len(common_words) * 0.1
            
            if score > 0:
                candidate_scenes.append((i, score, len(story)))
        
        if not candidate_scenes:
            return -1
        
        # 점수가 높고, story 길이가 짧은 순으로 정렬
        candidate_scenes.sort(key=lambda x: (-x[1], x[2]))
        
        return candidate_scenes[0][0]

    def _insert_missing_sentence(self, scene: Dict, missing_part: List[str]) -> Dict:
        """
        scene의 story에 누락된 문장을 적절한 위치에 삽입한다
        
        Args:
            scene (Dict): scene 데이터
            missing_part (List[str]): [앞문장, 누락문장, 뒷문장]
            
        Returns:
            Dict: 수정된 scene 데이터
        """
        prev_sentence, missing_sentence, next_sentence = missing_part
        story = scene.get('story', '')
        
        # 문장 끝에 마침표가 없으면 추가
        def ensure_period(sentence):
            if sentence and not sentence.rstrip().endswith(('.', '!', '?')):
                return sentence.rstrip() + '.'
            return sentence
        
        missing_sentence = ensure_period(missing_sentence)
        
        # 앞문장 뒤에 삽입하는 경우
        if prev_sentence and prev_sentence in story:
            insert_pos = story.find(prev_sentence) + len(prev_sentence)
            # 공백과 마침표 처리
            separator = " " if not story[insert_pos:insert_pos+1].isspace() else ""
            new_story = story[:insert_pos] + separator + missing_sentence + story[insert_pos:]
            scene['story'] = new_story
            return scene
        
        # 뒷문장 앞에 삽입하는 경우
        if next_sentence and next_sentence in story:
            insert_pos = story.find(next_sentence)
            # 공백과 마침표 처리
            separator = " " if not story[insert_pos-1:insert_pos].isspace() else ""
            new_story = story[:insert_pos] + missing_sentence + separator + story[insert_pos:]
            scene['story'] = new_story
            return scene
        
        # 적절한 위치를 찾지 못한 경우 끝에 추가
        # story 끝에 마침표가 있는지 확인하고 공백 처리
        story = story.rstrip()
        if story and not story.endswith(('.', '!', '?')):
            story += '.'
        
        scene['story'] = story + " " + missing_sentence
        return scene

    def _fix_missing_parts(self, basic_scenes_data: Dict, missing_parts: List[List[str]]) -> Dict:
        """
        누락된 부분들을 기본 장면 데이터에 추가한다
        
        Args:
            basic_scenes_data (Dict): 기본 장면 데이터
            missing_parts (List[List[str]]): 누락된 부분들의 리스트
            
        Returns:
            Dict: 수정된 장면 데이터
        """
        scenes = basic_scenes_data.get("scenes", [])
        
        for missing_part in missing_parts:
            target_scene_idx = self._find_target_scene_for_missing_part(missing_part, scenes)
            
            if target_scene_idx >= 0:
                scenes[target_scene_idx] = self._insert_missing_sentence(
                    scenes[target_scene_idx], missing_part
                )
                print(f"누락 문장 '{missing_part[1][:50]}...' 을(를) Scene {target_scene_idx + 1}에 추가했습니다.")
            else:
                print(f"누락 문장 '{missing_part[1][:50]}...' 의 적절한 위치를 찾지 못했습니다.")
        
        return basic_scenes_data

    def _parse_basic_scenes_with_correction(self, text_content: str):
        """
        텍스트를 분석하여 장면별 기본 데이터를 생성하고,
        각 scene의 story를 합쳐 원본 story와 비교하여 불일치 시 한번만 직접 수정

        Args:
            text_content (str): 분석할 텍스트 내용

        Returns:
            dict: 개선된 기본 장면 데이터 (scene 배열 포함)
        """
        try:
            # 1. 기본 장면 파싱
            basic_scenes_data = self._parse_basic_scenes(text_content)
            
            # 2. scene의 story를 순서대로 합쳐 전체 story 재생성
            reconstructed_story = " ".join([scene["story"] for scene in basic_scenes_data.get("scenes", [])])
            
            # 3. 원본 story와 비교
            original_story = text_content.strip()
            reconstructed_story = reconstructed_story.strip()

            if reconstructed_story == original_story:
                print("Story 재구성 성공!")
                return basic_scenes_data
            else:
                print("Story 불일치 발견, 직접 수정 진행")
                
                # 4. 누락된 부분들을 찾기
                missing_parts = self._find_missing_parts(original_story, reconstructed_story)
                
                if missing_parts:
                    print(f"총 {len(missing_parts)}개의 누락된 부분을 발견했습니다.")
                    
                    # 5. 누락된 부분들을 적절한 scene에 추가
                    basic_scenes_data = self._fix_missing_parts(basic_scenes_data, missing_parts)
                    print("누락 부분 수정 완료!")
                else:
                    print("누락된 부분을 찾지 못했습니다.")
                
                return basic_scenes_data

        except Exception as e:
            print(f"기본 장면 파싱 오류: {e}")
            return basic_scenes_data

    def _infer_locations(self, basic_scenes_data: Dict[str, Any]) -> List[str]:
        """
        장면별 story 내용을 기반으로 각 장면의 location 추론
        
        Returns:
            List[str]: 각 장면의 위치 정보 리스트
        """
        try:
            # 장면별 요약 정보 생성
            scene_summaries = []
            scenes = basic_scenes_data.get("scenes", [])
            
            for i, scene in enumerate(scenes, 1):
                summary = f"Scene {i}: {scene.get('story', '')}"
                scene_summaries.append(summary)
            
            # 전체 장면 요약을 하나의 문자열로 결합
            scenes_context = "\n\n".join(scene_summaries)
            
            # location 추론 요청
            locations_str = self._request_location_inference(scenes_context, len(scenes))
            
            # LLM 반환 문자열을 실제 리스트로 변환
            locations = json.loads(locations_str)
            
            # 리스트가 아닌 경우 기본값으로 처리
            if not isinstance(locations, list):
                print(f"위치 추론 결과가 예상 형식이 아닙니다: {type(locations)}")
                return ["알 수 없음"] * len(scenes)
            
            # 장면 수와 위치 수가 일치하지 않는 경우 조정
            if len(locations) != len(scenes):
                print(f"위치 수({len(locations)})와 장면 수({len(scenes)})가 일치하지 않습니다.")
                if len(locations) < len(scenes):
                    # 부족한 경우 "알 수 없음"으로 채움
                    locations.extend(["알 수 없음"] * (len(scenes) - len(locations)))
                else:
                    # 초과한 경우 잘라냄
                    locations = locations[:len(scenes)]
            
            return locations
            
        except json.JSONDecodeError as e:
            print(f"위치 추론 결과 JSON 파싱 오류: {e}")
            scenes_count = len(basic_scenes_data.get("scenes", []))
            return ["알 수 없음"] * scenes_count
        except Exception as e:
            print(f"위치 추론 중 오류 발생: {e}")
            # 오류 발생 시 기본값으로 처리
            scenes_count = len(basic_scenes_data.get("scenes", []))
            return ["알 수 없음"] * scenes_count

    def _request_location_inference(self, scenes_context: str, scene_count: int) -> str:
        """
        전체 장면 컨텍스트를 고려하여 각 장면의 location 추론 요청
        
        Returns:
            str: JSON 형태의 위치 배열 문자열
        """
        location_instruction = f'''
        You are a location inference expert. You will receive scene summaries from a story and need to infer the most appropriate location for each scene.

        Analyze the full context of all scenes and determine where each scene takes place. Consider the following:

        1. Character actions and dialogue within each scene
        2. Environmental clues and descriptions
        3. The overall story flow and character movements between scenes
        4. Time progression and setting changes
        5. Logical connections between scenes

        Output:
        An array of exactly {scene_count} locations, one for each scene in order.

        Expected output format:
        ["location1", "location2", "location3", ...]
        '''

        caution = f"Return only a valid JSON array with exactly {scene_count} location strings. Do not include any explanatory text before or after the array."
        
        instruction = self.llm_helper_location.build_instruction(location_instruction, scenes_context, caution)
        return self.llm_helper_location.retry_and_extract(instruction, description="장면별 위치 추론")

    def _merge_locations(self, basic_scenes_data: Dict[str, Any], locations: List[str]) -> Dict[str, Any]:
        """
        기본 장면 데이터에 위치 정보를 추가
        
        Args:
            basic_scenes_data (Dict[str, Any]): 기본 장면 데이터
            locations (List[str]): 각 장면의 위치 정보
            
        Returns:
            Dict[str, Any]: 위치 정보가 추가된 장면 데이터
        """
        try:
            scenes = basic_scenes_data.get("scenes", [])
            
            # 각 장면에 location 추가
            for i, scene in enumerate(scenes):
                if i < len(locations):
                    scene["location"] = locations[i]
                else:
                    scene["location"] = "알 수 없음"
            
            # 전체 위치 목록도 추가
            basic_scenes_data["locations"] = locations
            
            return basic_scenes_data
            
        except Exception as e:
            print(f"위치 정보 병합 중 오류 발생: {e}")
            # 오류 발생 시 기본값으로 처리
            scenes = basic_scenes_data.get("scenes", [])
            for scene in scenes:
                scene["location"] = "알 수 없음"
            basic_scenes_data["locations"] = ["알 수 없음"] * len(scenes)
            return basic_scenes_data