from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import json

class PromptMakerInterface(ABC):
    """
    이미지 생성 프롬프트 메이커를 위한 인터페이스
    장면 데이터를 받아 이미지 생성에 적합한 프롬프트를 생성합니다.
    """
    
    @abstractmethod
    def make_prompt(self, scene: str, scene_index: int) -> dict:
        """
        장면 데이터를 받아서 이미지 생성 프롬프트를 생성합니다.
        
        Args:
            scene (str): 장면 정보가 포함된 문자열
            scene_index (int): 장면 번호
            
        Returns:
            str: 생성된 프롬프트 (JSON 형태의 문자열)
        """
        pass
    
        """
        생성된 응답이 유효한 JSON 형태인지 검증합니다.
        
        Args:
            response (str): 검증할 응답 문자열
            
        Returns:
            bool: 유효한 응답인지 여부
        """
        try:
            parsed = json.loads(response)
            
            # 필수 필드 검증
            required_fields = [
                'success', 'message', 'generated_prompt', 'prompt_type', 
                'keywords', 'estimated_length', 'prompt_quality_score'
            ]
            
            for field in required_fields:
                if field not in parsed:
                    return False
            
            # 데이터 타입 검증
            if not isinstance(parsed['success'], bool):
                return False
            if not isinstance(parsed['keywords'], list):
                return False
            if not isinstance(parsed['estimated_length'], int):
                return False
            if not isinstance(parsed['prompt_quality_score'], (int, float)):
                return False
            
            return True
            
        except (json.JSONDecodeError, KeyError, TypeError):
            return False
    