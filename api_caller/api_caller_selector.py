from llama_tools.llama_api_caller import LlamaAPICaller


class APICallerSelector:
    @staticmethod
    def select(api_type: str, **kwargs):
        if api_type == "llama":
            return LlamaAPICaller(**kwargs).get_call_api_fn()
        # elif caller_type == "openai":
        #     return OpenAIApiCaller(api_key=kwargs["api_key"])  # 예시
        raise ValueError(f"Unknown API type: {api_type}")

