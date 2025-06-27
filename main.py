# main.py
from constants.results_storage_paths.paths import *

# 1. OCR
from ocr.ocr_selector import OCRSelector
from ocr.ocr_manager import OCRManager

# 2. Translator
from translator.translator_selector import TranslatorSelector
from translator.translator_manager import TranslatorManager

# 3. Story Writer
from story_writer.story_writer_selector import StoryWriterSelector
from story_writer.story_writer_manager import StoryWriterManager

# 4. Scene Parser
from scene_parser.scene_parser_selector import SceneParserSelector
from scene_parser.scene_parser_manager import SceneParserManager

# 5-1. Prompt Maker
from prompt_maker.prompt_maker_selector import PromptMakerSelector
from prompt_maker.prompt_maker_manager import PromptMakerManager

# 5-2. Emotion Classifier
from emotion_classifier.emotion_classifier_selector import EmotionClassifierSelector
from emotion_classifier.emotion_classifier_manager import EmotionClassifierManager

# 6. Object Analyst
from object_analyst.object_analyst_selector import ObjectAnalystSelector
from object_analyst.object_analyst_manager import ObjectAnalystManager

# 6. Image Maker
from image_maker.image_maker_selector import ImageMakerSelector
from image_maker.image_maker_manager import ImageMakerManager

# 입력/출력 경로 설정
WORK_DIR.mkdir(exist_ok=True)

# OCR
ocr_model = OCRSelector.get_reader("easyocr")
ocr_manager = OCRManager(ocr_model)
ocr_manager.process(INPUT_IMAGE, str(OCR_TXT_PATH))

# Translator
translator = TranslatorSelector.get_translator("ko-en")  # or "en-ko"
translator_manager = TranslatorManager(translator)
translator_manager.process(str(OCR_TXT_PATH), str(KO_EN_TRANSLATED_PATH))
'''
# Story Writer
story_writer = StoryWriterSelector.get_writer("llama")
story_manager = StoryWriterManager(story_writer)
story_manager.process(str(KO_EN_TRANSLATED_PATH), str(STORY_PATH))

# Scene Parser
scene_parser = SceneParserSelector.get_parser("basic")
scene_parser_manager = SceneParserManager(scene_parser)
scene_parser_manager.process(str(STORY_PATH), str(SCENE_PATH))

# Prompt Maker
prompt_maker = PromptMakerSelector.get_prompt_maker("llama")
prompt_manager = PromptMakerManager(prompt_maker)
prompt_manager.process(str(SCENE_PATH), str(PROMPT_PATH))

# Image Maker
image_maker = ImageMakerSelector.get_image_maker("dream_shaper")
image_manager = ImageMakerManager(image_maker)
image_manager.process(str(PROMPT_PATH), str(IMAGE_OUTPUT_PATH))

# Emotion Classifier
emotion_classifier = EmotionClassifierSelector.get_emotion_classifier("minilm")
emotion_manager = EmotionClassifierManager(emotion_classifier)
emotion_manager.process(str(SCENE_PATH), str(EMOTION_PATH))

# Object Analyst
object_analyst = ObjectAnalystSelector.get_object_analyst("llama")
object_analyst_manager = ObjectAnalystManager(object_analyst)
object_analyst_manager.process(str(PROMPT_PATH), str(OBJECT_ANALYST_PATH))


# Translator
translator = TranslatorSelector.get_translator("en-ko")  # or "en-ko"
translator_manager = TranslatorManager(translator)
translator_manager.process(str(SCENE_PATH), str(EN_KO_TRANSLATED_PATH))

print("\n✅ 전체 파이프라인 실행 완료!")
'''