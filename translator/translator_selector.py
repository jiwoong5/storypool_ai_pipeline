from translator.translator_interface import TranslatorInterface
from translator.marian_translator import MarianTranslator
from translator.nllb_translator import NLLBTranslator

class TranslatorSelector:
    @staticmethod
    def get_translator(language_pair: str) -> TranslatorInterface:
        """언어 쌍에 따라 적합한 번역기 객체를 반환"""
        if language_pair == 'en-ko':
            return NLLBTranslator()
        elif language_pair == 'ko-en':
            return MarianTranslator()
        else:
            raise ValueError(f"지원되지 않는 언어 쌍입니다: {language_pair}")

