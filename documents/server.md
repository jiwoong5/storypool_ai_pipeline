## 서버 구성
ai server 요구조건
- 사용자 요청을 최소한의 시간 안에 완결된 결과물로 제공

ai server 구현
- http api 요청
- 비동기 AI 작업 처리
- 메타 데이터 저장
- AI 모델 로딩 및 추론

병렬화
- 각 단계는 시퀀셜하게 실행되어야 함. 각 단계별로 gpu 사용량은 다를 수 있음
- 가령 어떤 단계는 cpu 처리량이 많아 gpu 를 상대적으로 덜 사용한다면, 병렬처리 없이 파이프라인 수행 시 gpu idle time 상승
- 각 단계를 독립된 작업으로 쪼개고 이를 병렬적으로 실행해 gpu idle time 을 낮춘다면 다량의 요청 처리 가능

