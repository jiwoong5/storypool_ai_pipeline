class LlamaHelper:
    def __init__(self, call_api_fn, delimiter: str = "---"):
        """
        :param call_api_fn: LLM 호출 함수 (str -> dict)
        :param delimiter: 추출 구분자
        """
        self.call_api = call_api_fn
        self.delimiter = delimiter

    def build_instruction(self, main_instruction: str, content: str, caution: str) -> str:
        return f"{main_instruction.strip()}\n{content.strip()}\n{caution.strip()}"

    def extract_between_delimiters(self, response: str) -> str:
        parts = response.split(self.delimiter)
        if len(parts) >= 3:
            return parts[1].strip()
        raise ValueError(
            f"Invalid delimiter count. Expected 2 delimiters '{self.delimiter}', "
            f"but found {len(parts) - 1}. Full response: {response}"
        )

    def retry_and_extract(self, instruction: str, max_retries: int = 3, description: str = "작업") -> str:
        for attempt in range(1, max_retries + 1):
            try:
                response = self.call_api(instruction)
                return self.extract_between_delimiters(response["response"])
            except ValueError as e:
                print(f"[{attempt}회차] Delimiter 오류 발생: {e}")
                if attempt == max_retries:
                    raise ValueError(f"최대 {max_retries}회 재시도했지만 실패했습니다. 중단합니다.")
                print(f"다시 {description}을(를) 시도합니다...")
        raise ValueError("예상치 못한 오류로 실패했습니다.")
