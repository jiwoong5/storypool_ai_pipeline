from story_writer.story_writer_interface import StoryWriterInterface
from story_writer.llama_story_writer import LlamaStoryWriter

class StoryWriterSelector:
    @staticmethod
    def get_writer(writer_type: str = "llama", **kwargs) -> StoryWriterInterface:
        if writer_type == "llama":
            return LlamaStoryWriter(**kwargs)
        # 다른 작성기 추가 가능 (예: "gpt", "claude")
        raise ValueError(f"Unsupported writer type: {writer_type}")