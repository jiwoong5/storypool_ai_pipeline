from abc import ABC, abstractmethod
from typing import Dict, List
import json

class PromptMakerInterface(ABC):
    """
    이미지 생성 프롬프트 메이커를 위한 인터페이스
    장면 데이터를 받아 이미지 생성에 적합한 프롬프트를 생성합니다.
    """

    @abstractmethod
    def make_prompts(self, scenes: List[str]) -> List[Dict]:
        """여러 장면에 대해 프롬프트들을 한꺼번에 생성합니다."""
        pass
    