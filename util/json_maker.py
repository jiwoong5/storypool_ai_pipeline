import json
import re
from typing import Dict, Any


class JsonMaker:
    """JSON 추출 및 형식 수정을 담당하는 클래스"""
    
    def str_to_json(self, response: str) -> str:
        """
        문자열에서 JSON 부분만 추출
        
        Args:
            response (str): LLM 응답 문자열
            
        Returns:
            str: 추출된 JSON 문자열
        """
        # JSON 코드 블록에서 추출
        json_match = re.search(r'```json\s*(.*?)\s*```', response, re.DOTALL)
        if json_match:
            return json_match.group(1).strip()
        
        # 일반 코드 블록에서 추출
        json_match = re.search(r'```\s*(.*?)\s*```', response, re.DOTALL)
        if json_match:
            content = json_match.group(1).strip()
            # JSON 형태인지 확인
            if content.startswith('{') and content.endswith('}'):
                return content
        
        # JSON 객체 패턴 찾기 (가장 외부 중괄호)
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if json_match:
            return json_match.group(0).strip()
        
        return response.strip()
    
    def fix_json_format(self, json_str: str) -> str:
        """
        일반적인 JSON 형식 오류 수정
        
        Args:
            json_str (str): 수정할 JSON 문자열
            
        Returns:
            str: 수정된 JSON 문자열
        """
        # trailing comma 제거
        json_str = re.sub(r',\s*}', '}', json_str)
        json_str = re.sub(r',\s*]', ']', json_str)
        
        # single quote를 double quote로 변경
        json_str = re.sub(r"'", '"', json_str)
        
        # 다중 공백 정리
        json_str = re.sub(r'\s+', ' ', json_str)
        
        # 불필요한 백슬래시 제거
        json_str = re.sub(r'\\(?!["\\/bfnrt])', '', json_str)
        
        return json_str.strip()
    
    def extract_and_parse_json(self, response: str) -> Dict[str, Any]:
        """
        문자열에서 JSON을 추출하고 파싱하여 딕셔너리로 반환
        
        Args:
            response (str): LLM 응답 문자열
            
        Returns:
            Dict[str, Any]: 파싱된 JSON 딕셔너리
            
        Raises:
            json.JSONDecodeError: JSON 파싱 실패 시
        """
        # JSON 추출
        json_str = self.str_to_json(response)
        
        # 형식 수정
        json_str = self.fix_json_format(json_str)
        
        print(json_str)
        # JSON 파싱
        return json.loads(json_str)
    
    def is_valid_json(self, json_str: str) -> bool:
        """
        JSON 문자열이 유효한지 확인
        
        Args:
            json_str (str): 검증할 JSON 문자열
            
        Returns:
            bool: 유효한 JSON이면 True, 아니면 False
        """
        try:
            json.loads(json_str)
            return True
        except json.JSONDecodeError:
            return False