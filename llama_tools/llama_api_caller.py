from typing import Callable, Dict, Any
import requests

class LlamaAPICaller:
    def __init__(self, model: str, api_url: str):
        self.model = model
        self.api_url = api_url

    def get_call_api_fn(self) -> Callable[[str], Dict[str, Any]]:
        def call_api(instruction: str) -> Dict[str, Any]:
            data = {
                "model": self.model,
                "prompt": instruction,
                "stream": False
            }
            response = requests.post(self.api_url, json=data)
            response.raise_for_status()
            return response.json()

        return call_api
