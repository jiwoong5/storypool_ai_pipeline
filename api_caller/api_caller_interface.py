from abc import ABC, abstractmethod
from typing import Dict, Any

class APICallerInterface(ABC):
    @abstractmethod
    def get_call_api_fn(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        :param payload: API 호출에 사용할 데이터
        :return: API 호출 함수
        """
        pass
