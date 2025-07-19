from translator.translator_interface import TranslatorInterface

class TranslatorManager:
    def __init__(self, translator: TranslatorInterface):
        self.translator = translator

    def process(self, input_text: str) -> str:
        """
        Translate the given text string and return the result.
        """
        translated = self.translator.translate_text(input_text)
        return translated

    def process_from_path(self, input_path: str, output_path: str) -> str:
        """
        Read text from file, translate it, and write result to output file.
        """
        with open(input_path, 'r', encoding='utf-8') as f:
            text = f.read()

        translated = self.process(text)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(translated)

        return translated