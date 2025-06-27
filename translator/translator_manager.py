from translator.translator_interface import TranslatorInterface

class TranslatorManager:
    def __init__(self, translator: TranslatorInterface):
        self.translator = translator

    def process(self, input_path: str, output_path: str):
        # 파일 읽기
        with open(input_path, 'r', encoding='utf-8') as f:
            text = f.read()
        # 번역
        translated = self.translator.translate_text(text)
        # 파일 쓰기
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(translated)
        return translated