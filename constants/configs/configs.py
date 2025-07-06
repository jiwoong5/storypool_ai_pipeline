from dataclasses import dataclass

# Pipeline Configuration
@dataclass
class PipelineConfig:
    ocr_reader_type: str = "easyocr"
    translator_type: str = "marian"
    story_writer_type: str = "llama"
    scene_parser_type: str = "llama"
    prompt_maker_type: str = "llama"
    image_maker_type: str = "dream_shaper"
    continue_on_error: bool = True
    save_intermediate: bool = True