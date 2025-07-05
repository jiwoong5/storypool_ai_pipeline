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
```

- 프롬프트 엔지니어링은 작업의 목적과 품질, 비용/속도를 trade-off하며 설계

LlamaSceneParser 응답 핵심 요소 
- scene number: 장면번호 ex) 1
- scene_title: 장면 제목 ex) "getting ready at home"
- characters: 등장인물. ex) ["Narrator", "mom", "daughter",]
- location: 배경 ex) "home"
- time: 시간 ex) "morning"
- mood: 분위기 ex) "calm"
- summary: "i finished getting ready at home in the morning to go to the park"
- dialogue_count: 대화 수 ex) 0

LlamaSceneParser 프롬프트 엔지니어링 분석
- LlamaSceneParser에서 사용하는 프롬프트를 프롬프트 엔지니어링의 7가지 단계로 분석

1. 주요 목적
- **텍스트 장면 분할**: 주어진 텍스트를 논리적으로 장면별로 나누기
- **구조화된 정보 추출**: 각 장면의 핵심 요소들을 체계적으로 추출
- **JSON 형태 출력**: 구조화된 데이터로 변환하여 프로그래밍적 활용 가능

구체적 작업
1. 전체 스토리 읽기 및 장면 전환점 식별
2. 각 장면별 등장인물, 위치, 시간, 분위기 분석
3. 대화 존재 시 대화 수 계산
4. 각 장면을 한 문장으로 요약

2. 모델 태도/역할 지시 (Role Prompting)

역할 설정
- "You are a professional story analyst."

태도 지시
- 전문성 강조: "professional" 키워드로 전문적 분석 요구
- 체계적 접근: "carefully read", "logically divide", "accurately extract" 등으로 신중하고 논리적인 분석 요구
- 단계적 작업: "follow these steps" 지시로 구조화된 분석 과정 제시

전문성 부여 효과
- 모델이 일반적인 텍스트 생성이 아닌 전문적 분석 모드로 전환
- 보다 체계적이고 구조화된 결과 생성 유도


3. 출력 형식 요구 (Output Format)

강력한 형식 지시
- "IMPORTANT: Return ONLY valid JSON format without any additional text or explanation."
- "Return only valid JSON format. Do not include any explanatory text before or after the JSON."
- 구체적 JSON 스키마 제시
```json
{
  "scenes": [
    {
      "scene_number": 1,
      "scene_title": "Getting ready at home",
      "characters": ["Narrator"],
      "location": "Home",
      "time": "Morning",
      "mood": "Calm",
      "summary": "I finished getting ready at home in the morning to go to the park.",
      "dialogue_count": 0
    }
  ],
  "total_scenes": 1,
  "main_characters": ["Narrator"],
  "locations": ["Home"]
}
```

형식 준수 강화
- 중복 강조: 여러 번 JSON 형식 준수 요구
- 구체적 예시: 정확한 JSON 구조 제시
- 명확한 금지사항: 추가 텍스트 금지 명시


4. 작업 방식 선택 (Task Approach)
- 선택된 방식: Few-shot + CoT (Chain of Thought)

Few-shot Learning (one-shot)
- 구체적 예시 제공: JSON 형식의 완전한 예시 제시
- 패턴 학습: 예시를 통해 원하는 출력 형태 학습

Chain of Thought (CoT)
- 1. First, read the entire story and identify the scene transition points.
- 2. For each scene, analyze and extract the characters, location, time, and mood.
- 3. If there is dialogue, count the number of dialogue instances.
- 4. Summarize each scene in one sentence.

장면 분할 기준 제시
- Change of location (e.g., moving from home to the park)
- Passage of time (e.g., from morning to afternoon)
- Change of main activity (e.g., walking → playing → eating)
- Change in characters
  
방식 선택 이유
- 복잡한 분석 작업: 단순 zero-shot보다 단계적 접근 필요
- 일관성 확보: 명확한 기준과 절차 제시로 일관된 결과 유도
- 오류 방지: 구조화된 접근으로 누락이나 실수 최소화


5. Randomness 조절 (Temperature/Top-p)
- 현재 상태: temperature: 0.7, top-p: 0.9
- 설정이유: 일반적인 상태로 초기화해놨고 추후 조정 예정

조절시 고려사항
- 결정론적 결과 필요: 텍스트 분석은 창의성보다 정확성이 중요
- API 안정성: 예측 가능한 JSON 출력 필요
- 일관성 유지: 같은 텍스트에 대해 일관된 분석 결과 필요
- python# 권장 설정 (만약 추가한다면)
- temperature = 0.3    # 낮은 창의성, 높은 일관성
- top_p = 0.9         # 적절한 다양성 유지

향후 개선 방향
- 작업 유형별 조절: 창의적 요약 vs 사실적 분석에 따라 다른 설정
- 성능 테스트: 다양한 temperature 값에서 일관성 테스트 필요


6. 추가 보정 (Self-consistency/Post-processing)

현재 구현된 Post-processing: ScenePostProcessor 클래스

```python
class ScenePostProcessor:
    def clean_llm_response(self, response: str) -> str:
        # JSON 코드 블록 추출
        # JSON 객체 패턴 찾기
        
    def normalize_character_names(self, characters: List[str]) -> List[str]:
        # 등장인물 이름 정규화
        
    def validate_scene_number(self, scenes: List[Dict]) -> List[Dict]:
        # 장면 번호 검증 및 수정
        
    def fix_json_format(self, json_str: str) -> str:
        # JSON 형식 오류 수정
```

에러 처리 및 재시도
```python
raw_data = self.llm_helper.retry_and_get_json(instruction, description="장면 분석")
```

보정 방식의 장점
- JSON 파싱 오류 방지: 다양한 형식의 응답에서 JSON 추출
- 데이터 정규화: 등장인물 이름 통일, 장면 번호 검증
- 오류 복구: 일반적인 JSON 형식 오류 자동 수정
- 재시도 메커니즘: 실패 시 자동 재시도로 안정성 향상


개선 가능 영역
- Temperature 조절: 작업 유형에 따른 세밀한 조절
- Self-consistency: 여러 번 생성 후 일관성 검증
- Dynamic prompting: 텍스트 길이나 복잡도에 따른 프롬프트 조정
- Multi-pass processing: 초기 분석 후 재검토 단계 추가


결론
- LlamaSceneParser의 프롬프트는 구조화된 텍스트 분석이라는 명확한 목적을 위해 체계적으로 설계
- 특히 Few-shot + CoT 방식과 강력한 후처리를 통해 일관성 있고 정확한 결과를 생성하는 것이 핵심 전략
- 현재 설계는 안정성과 정확성에 중점을 두고 있으며, 향후 randomness 조절과 self-consistency 도입을 통해 더욱 개선될 수 있음
