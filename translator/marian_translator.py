from translator.translator_interface import TranslatorInterface
from transformers import MarianMTModel, MarianTokenizer
import re

class MarianTranslator(TranslatorInterface):
    def __init__(self, model_name='Helsinki-NLP/opus-mt-ko-en'):
        self.model_name = model_name
        self.tokenizer = MarianTokenizer.from_pretrained(model_name)
        self.model = MarianMTModel.from_pretrained(model_name)
    
    def split_sentences(text):
        return re.split(r'(?<=[.!?])\s+', text)

    def translate_text(self, text: str) -> str:
        # KSS로 문장 분리
        sentences = self.split_sentences(text)

        # 번역 수행
        translated_sentences = []
        for sentence in sentences:
            inputs = self.tokenizer(sentence, return_tensors="pt", padding=True, truncation=True)
            translated = self.model.generate(**inputs)
            result = self.tokenizer.decode(translated[0], skip_special_tokens=True)
            translated_sentences.append(result)

        # 최종 번역 결과를 하나의 문자열로 합침
        final_result = " ".join(translated_sentences)
        return final_result

# 메인 가드
if __name__ == "__main__":
    sample_text = "제 미쿡친구 줴임스에게 6마눠을 송금하구 시풔요"

    translator = MarianTranslator()
    result = translator.translate_text(sample_text)

    print("=== 번역 결과 ===")
    print(result)
