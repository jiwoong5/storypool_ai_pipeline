import redis
import time
import uuid

from translator.translator_selector import TranslatorSelector
from translator.translator_manager import TranslatorManager
from story_writer.story_writer_selector import StoryWriterSelector
from story_writer.story_writer_manager import StoryWriterManager
from scene_parser.scene_parser_selector import SceneParserSelector
from scene_parser.scene_parser_manager import SceneParserManager
from prompt_maker.prompt_maker_selector import PromptMakerSelector
from prompt_maker.prompt_maker_manager import PromptMakerManager
from emotion_classifier.emotion_classifier_selector import EmotionClassifierSelector
from emotion_classifier.emotion_classifier_manager import EmotionClassifierManager
from image_maker.image_maker_selector import ImageMakerSelector
from image_maker.image_maker_manager import ImageMakerManager

# Redis 연결
r = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)

# translator 로직
def ko_en_translator(input_text:str):
    translator = TranslatorSelector.get_translator("marian")
    translator_manager = TranslatorManager(translator)
    return translator_manager.process(input_text)

if __name__ == "__main__":
    print(ko_en_translator("안녕 망할 세상"))


