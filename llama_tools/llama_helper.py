from typing import Dict
import json
from util.json_maker import JsonMaker


class LlamaHelper:
    """LLM 호출 및 응답 처리를 담당하는 헬퍼 클래스"""
    
    def __init__(self, call_api_fn, temperature=0.4, top_p=0.9):
        """
        Args:
            call_api_fn: LLM 호출 함수 (str -> dict)
        """
        self.call_api = call_api_fn
        self.temperature = temperature
        self.top_p = top_p
        self.json_maker = JsonMaker()

    def build_instruction(self, main_instruction: str, content: str, caution: str) -> str:
        """
        지시사항, 내용, 주의사항을 조합하여 최종 instruction 생성
        
        Args:
            main_instruction (str): 주요 지시사항
            content (str): 분석할 내용
            caution (str): 주의사항
            
        Returns:
            str: 조합된 instruction
        """
        # 특수기호 주의사항 추가
        special_char_notice = "※ When using special characters in strings make sure to escape them."
        
        return f"{main_instruction.strip()}\n{content.strip()}\n{caution.strip()}\n{special_char_notice}"


    def retry_and_extract(self, instruction: str, max_retries: int = 3, description: str = "작업") -> str:
        """
        LLM 호출을 재시도하며 텍스트 응답을 추출
        
        Args:
            instruction (str): LLM에 전달할 지시사항
            max_retries (int): 최대 재시도 횟수
            description (str): 작업 설명 (로깅용)
            
        Returns:
            str: LLM 응답 텍스트
            
        Raises:
            ValueError: 최대 재시도 횟수 초과 시
        """
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
        """
        LLaMA API 호출 결과를 안전하게 JSON으로 파싱하여 반환합니다.
        - Python dict, 순수 JSON 문자열, Python dict 스타일 문자열 모두 처리
        - description이 'story 개선 요청'일 경우 raw response 출력
        - 실패 시 최대 max_retries 회 재시도
        """
        for attempt in range(1, max_retries + 1):
            try:
                # API 호출
                response = self.call_api(instruction)
                json_data = response["response"]

                # 이미 dict이면 그대로 반환
                if isinstance(json_data, dict):
                    return json_data

                # 문자열로 변환
                json_str = str(json_data).strip()

                # Python dict 스타일 문자열 처리
                if json_str.startswith("{") and json_str.endswith("}"):
                    import ast
                    try:
                        data_dict = ast.literal_eval(json_str)
                        return data_dict
                    except Exception:
                        pass

                # JSON 파싱 시도
                return json.loads(json_str)

            except (json.JSONDecodeError, ValueError, SyntaxError) as e:
                print(f"[{attempt}회차] JSON 파싱 실패: {e}")
                if attempt == max_retries:
                    raise ValueError(f"최대 {max_retries}회 재시도했지만 실패했습니다. 중단합니다.")
                print(f"다시 {description}을(를) 시도합니다...")

            except Exception as e:
                print(f"[{attempt}회차] 기타 오류: {e}")
                if attempt == max_retries:
                    raise
                print(f"다시 {description}을(를) 시도합니다...")

