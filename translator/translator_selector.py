from translator.translator_interface import TranslatorInterface
from translator.marian_translator import MarianTranslator
from translator.nllb_translator import NLLBTranslator

class TranslatorSelector:
    @staticmethod
    def get_translator(translator: str) -> TranslatorInterface:
        """언어 쌍에 따라 적합한 번역기 객체를 반환"""
        if translator == 'nllb':
            return NLLBTranslator()
        elif translator == 'marin':
            return MarianTranslator()
        else:
            raise ValueError(f"지원되지 않는 번역기입니다: {translator}")

