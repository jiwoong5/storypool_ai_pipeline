from prompt_maker.llama_prompt_maker import LlamaPromptMaker

class PromptMakerSelector:
    @staticmethod
    def get_prompt_maker(model_type: str):
        if model_type == "llama":
            return LlamaPromptMaker()
        else:
            raise ValueError(f"지원되지 않는 모델 타입: {model_type}")
