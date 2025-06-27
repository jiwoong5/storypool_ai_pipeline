from object_analyst.llama_object_analyst import LlamaObjectAnalyst

class ObjectAnalystSelector:
    @staticmethod
    def get_object_analyst(model_type: str):
        if model_type == "llama":
            return LlamaObjectAnalyst()
        else:
            raise ValueError(f"지원되지 않는 모델 타입: {model_type}")
