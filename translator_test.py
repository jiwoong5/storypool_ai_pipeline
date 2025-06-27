from translator.translator_selector import TranslatorSelector
from translator.translator_manager import TranslatorManager

if __name__ == "__main__":
    language_pair = "en-ko"

    translator = TranslatorSelector.get_translator(language_pair)

    manager = TranslatorManager(translator)

    translated_text = manager.process("translator/input_en.txt", "translator/result.txt")

    print("번역 완료! output.txt에 저장되었습니다.")

