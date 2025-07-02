## 핵심용어
Prompt
- 모델에게 작업 지시를 내리기 위한 입력 문장 또는 문서
- 질문, 명령, 데이터 형식 등 다양한 형태
- ex) "다음 문장을 요약해줘: {텍스트}"

Zero-shot
- 모델에게 사전 예시 없이 바로 작업을 시키는 방식
- LLM이 사전 학습된 일반 지식을 기반으로 답변
- 특징: 간단, 빠름, 답변 품질이 일정하지 않거나 모호할 수 있음

Few-shot
- 작업 예시(샘플)를 몇 개 포함한 프롬프트 제공
- 모델이 예시를 보고 패턴을 학습한 것처럼 답변
- 특징: 품질 향상, 일관성 증가, 프롬프트 길이 증가 → token 비용/제약
```plaintext
문장을 영어로 번역해:
한글: 안녕하세요
영어: Hello

한글: 감사합니다
영어:
```

Chain-of-thought (CoT)
- 모델이 중간 추론 단계를 거치며 답을 도출하도록 지시
- 일종의 "생각하는 과정을 써보게 하는 프롬프트"
- 특징: 논리적 문제 해결, 수학, 복잡한 reasoning에 유용, 답변 길어짐
```plaintext
문제를 푸는 과정을 단계별로 설명하고 마지막에 답을 알려줘.
```

Self-consistency
- 같은 질문에 대해 여러 답변을 생성 → 그 중 가장 일관된 답 선택
- CoT와 함께 쓰이는 경우 많음
- 특징: 답변 신뢰성 향상, 여러 번 생성 → 비용/시간 증가

Temperature
- 모델 출력의 무작위성 정도 조절하는 파라미터
- 0에 가까울수록 일관성 ↑, 1 이상이면 다양성 ↑
- 특징: 0~0.3: 안정적, 예측 가능한 답, 0.7 이상: 창의적, 다양성, 높으면 hallucination 가능

hallucination
- LLM이 그럴듯하게 보이지만 사실과 다르거나 허구적인 정보를 생성하는 현상
- **사실적 오류**: 존재하지 않는 사람, 장소, 사건 언급
- **논리적 오류**: 숫자 계산, 논리적 추론이 틀림
- **출력 형식 위반**: JSON 형식을 요구했는데 문장으로 응답
- **근거 없는 창작**: 질문에 없던 정보를 지어냄

Top-p (nucleus sampling)
- 다음 단어 후보 중 누적 확률이 p 이하인 후보만 샘플링, temperature와 비슷한 randomness 조절 방법
- **누적 확률 (cumulative probability)**: 모델이 다음 단어 후보로 제안하는 단어들을 확률순으로 정렬한 뒤, 위에서부터 확률을 더해간 값의 합
- 특징: 불필요한 단어 제외하고도 창의성 유지, p 값 낮을수록 보수적

Multi-pass / Multi-stage
- 작업을 한 번에 끝내지 않고 여러 단계로 나눠 프롬프트 작성
- 각 pass에서 다른 목표 수행
- 특징: 정밀도, 품질 ↑, 검증 및 post-processing 용이, 속도 ↓, 설계 복잡

multi-pass vs chain-of-thought
- multi-pass의 각 단계는 인과관계가 없을 수도 있음.
- chain-of-thought 에서 다음단계 추론은 이전단계 추론 결과로부터 기인함.
- ex) mp 에서 각 pass는 장면 경계 구분, 각 장면별 등장인물 등으로 구성될 수 있음
- ex) chain-of-thought 에서 각 단계는 2*(1+1) 이라는 질문에서 1+1 = 2, 2*(1+1) = 2*2 = 4

System prompt / Role prompting
- 모델에게 역할, 태도, 스타일 지시
- 특히 API나 챗봇 설계에서 system prompt로 초기 세팅
- 예시: 너는 엄격한 품질관리자야. 답변은 반드시 근거를 포함해.

Output format specification
- 모델 출력 형식을 엄격히 지시
- JSON, 표, 리스트 등
- 특징: 파싱/후처리 용이, 모델이 형식을 깨뜨릴 경우 추가 검증 필요

단계적 사고 구조

```lua
1️. 목적 정의 (무엇을 시킬 것인가)
2️. 모델 태도/역할 지시 (role prompting, system prompt)
3️. 출력 형식 요구 (output format)
4️. 작업 방식 선택 (zero-shot / few-shot / CoT / multi-pass)
5️. randomness 조절 (temperature / top-p)
6. 추가 보정 (self-consistency / post-processing)
7. 요약
```

- 프롬프트 엔지니어링은 작업의 목적과 품질, 비용/속도를 trade-off하며 설계
