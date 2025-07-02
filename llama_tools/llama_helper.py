from typing import Dict
import json
import re

class LlamaHelper:
    def __init__(self, call_api_fn):
        """
        :param call_api_fn: LLM 호출 함수 (str -> dict)
        """
        self.call_api = call_api_fn

    def build_instruction(self, main_instruction: str, content: str, caution: str) -> str:
        return f"{main_instruction.strip()}\n{content.strip()}\n{caution.strip()}"

    def retry_and_extract(self, instruction: str, max_retries: int = 3, description: str = "작업") -> str:
        for attempt in range(1, max_retries + 1):
            try:
                response = self.call_api(instruction)
                # LLM 응답 dict 구조에서 response 필드만 바로 반환
                return response["response"].strip()
            except Exception as e:
                print(f"[{attempt}회차] 오류 발생: {e}")
                if attempt == max_retries:
                    raise ValueError(f"최대 {max_retries}회 재시도했지만 실패했습니다. 중단합니다.")
                print(f"다시 {description}을(를) 시도합니다...")
        raise ValueError("예상치 못한 오류로 실패했습니다.")

    def retry_and_get_json(self, instruction: str, max_retries: int = 3, description: str = "작업") -> Dict:
        for attempt in range(1, max_retries + 1):
            try:
                response = self.call_api(instruction)
                text = response["response"].strip()
                
                # PostProcessor의 clean_llm_response + fix_json_format 역할 통합
                text = self.post_process_json_string(text)
                
                # JSON 파싱
                return json.loads(text)
                
            except json.JSONDecodeError as e:
                print(f"[{attempt}회차] JSON 파싱 실패: {e}")
                if attempt == max_retries:
                    raise ValueError(f"최대 {max_retries}회 재시도했지만 실패했습니다. 중단합니다.")
                print(f"다시 {description}을(를) 시도합니다...")
            except Exception as e:
                print(f"[{attempt}회차] 기타 오류: {e}")
                if attempt == max_retries:
                    raise
                print(f"다시 {description}을(를) 시도합니다...")

    def post_process_json_string(self, text: str) -> str:
        # PostProcessor의 fix_json_format 로직을 이쪽으로 옮김
        text = re.sub(r'```json\s*', '', text)
        text = re.sub(r'```', '', text)
        text = re.sub(r',\s*}', '}', text)
        text = re.sub(r',\s*]', ']', text)
        text = re.sub(r"'", '"', text)
        return text.strip()