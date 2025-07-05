프롬프트 고려사항
1. 프롬프트 길이
- 프롬프트 길이가 너무 짧으면 (예: “cat”) 생성 이미지의 디테일과 품질이 낮아짐.
- 프롬프트에 추가 설명어(adjectives, style guides)가 포함되면 CLIPScore, aesthetic score 평균이 증가.
- 단, 너무 긴 프롬프트는 marginal gain만 제공하거나 오히려 품질을 저하시킬 수 있음 (장황한 프롬프트의 효과는 한계가 있음).

2. 스타일/작가 이름
- 특정 작가명 (예: “in the style of Van Gogh”) 추가 시 시각적 스타일의 일관성이 강화됨.
- 작가명이나 스타일 키워드는 CLIPScore보다 aesthetic score (미학적 품질)에 더 큰 영향.
- “4k, ultra-detailed, photorealistic”과 같은 키워드는 사진 품질을 높이는 데 매우 효과적.

3. 단어의 역할
- 명사(nouns): 생성 이미지의 주된 개체나 주제 결정
- 형용사(adjectives): 색, 질감, 느낌에 영향 (예: “shiny”, “dark”, “ethereal”)
- 부사(adverbs)와 구체적 배경 설명: 이미지 구도와 분위기 변화에 기여
- 불필요한 단어는 품질 저하 가능성 (예: 모호한 서술은 CLIPScore 저하)

4. 프롬프트 변화의 민감도
- 단일 단어(특히 스타일, 질감 관련) 제거/삽입 시 출력 이미지가 육안으로 명확히 다른 결과물로 변화.
- 가장 영향력이 큰 단어군: style keywords (e.g. oil painting, cyberpunk, concept art), quality keywords (e.g. ultra-realistic, 8K, highly detailed), lighting (e.g. dramatic lighting, soft shadows)

5. 정량 평가
- CLIPScore: 프롬프트와 이미지 간 의미적 일치도 측정 → 길이 늘리기보다는 핵심 키워드가 더 중요
- aesthetic score: 미학적 품질 측정 → 스타일 키워드, 화질 관련 키워드에 민감
- diversity score: 다양성은 길이가 너무 긴 프롬프트보다 짧고 집중된 프롬프트에서 더 높게 유지됨


프롬프트 최적화
1. 프롬프트 최적화 목적
- 모델이 이해하기 더 쉬운 프롬프트 작성 → 출력물 품질 향상
- 의미적 일치 (prompt 의미와 이미지 일치)
- aesthetic score (미적 품질) 향상
- 다양성 (diversity) 확보
- 때로는 adversarial prompt (모델의 취약점 노출용) 생성

2. 프롬프트 최적화의 방법
- 수작업(human engineering): 사람이 직접 키워드를 조합하거나 스타일 이름 추가 ex) "cat" → "A photorealistic 4k portrait of a fluffy cat with blue eyes, studio lighting"
- 자동 최적화: 강화학습 기반 최적화 (예: Microsoft Promptist), 진화적 탐색 (evolutionary search), discrete prompt space optimization (예: On Discrete Prompt Optimization for Diffusion Models), LLM 기반 프롬프트 확장/개선

3. 프롬프트 최적화에서 다루는 변수
- 단어의 선택 (명사, 형용사, 스타일명, 작가명)
- 단어의 순서
- 단어의 길이/복잡도
- 불필요한 단어 제거
- 스타일/품질 관련 키워드 추가

캐릭터 일관성 유지 문제
- 동일 prompt를 여러 번 주더라도 생성된 이미지의 캐릭터 외형 (얼굴, 체형, 헤어스타일 등)이 매번 달라지는 문제
- diffusion 모델의 stochastic sampling + latent space 다양성 때문에 발생

1. Identity Clustering (정체성 클러스터링)
- 동일 prompt로 여러 이미지를 샘플링
- CLIP embedding space에서 이미지의 identity feature 벡터를 추출
- 이 feature 벡터들을 clustering → 주요 identity 그룹(클러스터)을 선택
- 주요 identity 클러스터의 중심을 target identity vector로 삼음

2. Iterative Refinement (반복적 정체성 강화)
- 선택된 identity vector에 가장 가까운 이미지들을 추가 샘플링
- 새로운 샘플에서 identity vector 업데이트
- 반복 → identity feature의 robustness 강화
- 최종적으로 target identity에 맞게 샘플링

3. Prompt Alignment (프롬프트 정합성)
- 캐릭터 identity를 유지하면서도 prompt 내용 (배경, 포즈 등)을 충실히 반영
- identity 유지와 prompt alignment 사이의 trade-off를 분석
- prompt alignment metric: CLIPScore + 사용자 평가

4. 평가 지표
- Identity consistency score: 생성된 이미지들의 CLIP embedding 간 cosine similarity
- Prompt consistency score: 이미지와 prompt 간 CLIPScore
- Human preference study: 사용자들이 캐릭터 일관성과 prompt 충실성을 얼마나 선호하는지 설문

5. 한계
- 계산 비용 높음 (초기 샘플링 + 반복 refinement 필요, 20분 이상 소요 가능)
- 일부 속성(의상, 표정 등)의 변화를 완전히 제어하지 못함
- latent space diversity 때문에 identity drift 가능
- CLIP embedding은 identity 특징 (얼굴, 주요 개체) + prompt context (포즈, 조명, 배경) 둘 다 포함 => prompt가 크게 다르면 context 차이가 embedding에 크게 영향을 미치고, character vector 비교가 부정확해짐

최적화된 프롬프트 생성 방향
- Scene 정보 추출 (주요 인물, 배경 등)
- 주요인물에 대한 외형 추출
- 주요 개체 + 행동 + 배경 + 스타일 + 품질 키워드로 구성된 프롬프트 생성 ([Identity anchor], [action/pose], [background], [style/quality keywords] 템플릿)
- identity vector 학습(50 ~ 100장)
- 생성된 이미지의 embedding과 기존 identity vector의 cosine similarity를 계산
- identity similarity loss 기반 re-ranking 또는 filtering 수행
- identity vector와 가장 유사한 embedding을 가진 샘플을 선택
- CLIPScore + aesthetic score + human check의 균형적 평가 및 프롬프트 정합성 계산
- 생성 종료 or 재생성 판단


참고자료
- [Investigating Prompt Engineering in Diffusion Models](https://arxiv.org/abs/2211.15462)
- [The Chosen One: Consistent Characters in Text‑to‑Image Diffusion Models](https://arxiv.org/abs/2311.10093?utm_source=chatgpt.com)
