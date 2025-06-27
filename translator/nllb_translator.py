from translator.translator_interface import TranslatorInterface
from transformers import pipeline
class NLLBTranslator(TranslatorInterface):
    def __init__(self, model_name='NHNDQ/nllb-finetuned-en2ko', device=0, src_lang='eng_Latn', tgt_lang='kor_Hang'):
        self.translator = pipeline(
            'translation',
            model=model_name,
            device=device,
            src_lang=src_lang,
            tgt_lang=tgt_lang
        )

    def translate_text(self, text: str) -> str:
        # 긴 텍스트를 여러 청크로 분할
        chunks = self.split_text(text)
        translated_chunks = []

        for chunk in chunks:
            output = self.translator(chunk, max_length=512)
            translated_chunks.append(output[0]['translation_text'])

        # 결과 병합
        return "\n".join(translated_chunks)

    def split_text(self, text, max_length=500):
        """텍스트를 max_length(단어 기준)로 분할하는 헬퍼 함수"""
        words = text.split()
        chunks = []
        current_chunk = []
        current_length = 0

        for word in words:
            if current_length + len(word) + 1 <= max_length:  # +1은 공백 고려
                current_chunk.append(word)
                current_length += len(word) + 1
            else:
                chunks.append(" ".join(current_chunk))
                current_chunk = [word]
                current_length = len(word)

        if current_chunk:
            chunks.append(" ".join(current_chunk))
        return chunks

# 메인 가드
if __name__ == "__main__":
    sample_text = "hello world. it's time to do coding"

    translator = NLLBTranslator()
    result = translator.translate_text(sample_text)

    print("=== 번역 결과 ===")
    print(result)