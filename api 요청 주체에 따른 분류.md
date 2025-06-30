## 현재 인증 구조
- storypool 의 인증 구조는 다음과 같음
```
클라이언트 로그인 → access token 획득
      ↓
API 요청 시 Authorization 헤더에 Bearer 토큰 추가
      ↓
토큰 검증
      ↓
성공: 인가된 동작 수행
실패: 401 Unauthorized 반환
```

## 토큰 검증 주체
- ai 파이프라인 서버
```
[Client] ---> [AI 파이프라인 서버 (FastAPI)]
                    └─> (인증 포함 + AI 처리)
```
- access token을 발행한 서버 (api gateway)
```
[Client] ---> [인증 서버(API Gateway)]
                     ↓
                [AI 파이프라인 서버 (FastAPI)]
```

## 토큰 검증 주체에 따른 장단점
ai 파이프라인 직접 인증 방식 장점
- 구조 단순 — API가 클라이언트 요청을 직접 받고 바로 처리
- 인증 + AI 처리 + 로깅 등 통합 관리 (코드도 한 프로젝트에서 가능)
- Latency 최소화 (api gateway -> ai 파이프라인 서버 투쿠션에 비해 네트워크 hop이 적음)
- **네트워크 hop**: 네트워크에서 한 장치(라우터, 스위치 등)에서 다음 장치로 패킷이 전달되는 과정에서의 한 단계

ai 파이프라인 직접 인증 방식 단점
- AI 파이프라인 서버가 보안 책임까지 짊어져야 함 (토큰 검증, 인증 실패 대응 등)
- 인증 코드와 AI 처리 코드가 섞여 관리 포인트가 복잡해짐 => 유지보수성 낮아짐
- 클라이언트가 AI 파이프라인 endpoint를 직접 보게 되어 endpoint 노출 위험 증가

간접 인증 방식 장점
- 보안 책임 분리 — 인증 서버에서 토큰 검증, 권한 관리, 속도 제한, 로깅 수행
- AI 파이프라인은 오직 AI 처리에 집중 가능 => 클린 코드, 유지보수 높아짐
- 클라이언트가 AI 파이프라인 endpoint를 직접 보지 않음 (보안 강화)
- 인증 서버에서 load balancing, caching, rate limiting 적용 용이

간접 인증 방식 단점
- 네트워크 hop이 추가 → 약간의 latency 증가 (대개 10~50ms 수준)
- 배포 구조가 복잡 (두 개 이상의 서비스 관리 필요)

### 직접인증 관련 단어
- Monolithic API (모놀리식 API): 인증, 권한, 비즈니스 로직, AI 처리까지 한 API 서비스에서 수행
- Self-authenticating API / API with embedded auth: API 자체에서 **JWT**/AccessToken 검증 포함
- All-in-One API: 보통 초기 프로토타입, POC, 소규모 서비스에서 기능이 분리되지 않은 api를 부르는 말
- Direct service endpoint: API 서비스에서 직접 인증하는 구조

### 간접인증 관련 단어
- API Gateway Pattern: 인증, 권한, 속도제한, 로깅, 라우팅 등을 Gateway에서 처리
- Backend for Frontend (BFF): 인증 서버가 클라이언트 요청을 AI 파이프라인으로 라우팅하며 인증/권한 처리
- Microservice Auth Gateway: AI 파이프라인은 인증에 관여하지 않는 마이크로서비스 구조
- Reverse Proxy Auth Architecture: Nginx, Envoy, API Gateway 등이 인증을 처리하고, AI 파이프라인에 프록시
- Zero-trust network pattern (서비스가 인증된 요청만 받음)

### 참고
보안 책임
- 접근 제어: 인가된 사용자/시스템만 접근 가능하도록 관리(인증, 권한 부여)
- 데이터 보호: 데이터 암호화, 기밀성/무결성 보장
- 네트워크 보안: 방화벽, IDS/IPS, VPN, API Gateway로 외부 위협 차단
- 로깅 및 모니터링: 이상 징후 탐지, 감사 로그 관리
- 취약점 관리: 보안 업데이트, 패치, 코드 취약점 점검
- 재해복구/백업: 사고 시 데이터 복구, 서비스 복구 계획 수립
- 규정/컴플라이언스: GDPR, ISO27001, NIST등 법적/산업 규제 준수
- 교육과 정책: 개발자/운영자 보안 교육, 정책 수립 및 준수

JWT (JSON Web Token)
- jwt: 클라이언트와 서버 간의 안전한 정보 교환 및 인증을 위해 사용하는 압축된 JSON 기반 토큰 => 무결성보장, 권한전달, 인증상태 유지 목적
- 서명(signature) 으로 변조 방지. 주로 인증(Authorization)과 정보 전달(Claims) 목적으로 사용.
- 구조: .으로 구분된 3개의 부분으로 구성
```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9. 
eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6Ik9uamlod29vbmciLCJpYXQiOjE1MTYyMzkwMjJ9. 
SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c
```
- Header (헤더): 토큰 타입(JWT), 서명 알고리즘 (예: HS256, RS256)
```json
{
  "alg": "HS256",
  "typ": "JWT"
}
```
- Payload (페이로드): 클레임(Claims), 표준 클레임 (iss, sub, exp, iat 등) + 사용자 정의 클레임
- 클레임(Claims): 사용자 정보, 권한, 유효기간 등
```json
{
  "sub": "1234567890",
  "name": "Onjihwoong",
  "iat": 1516239022
}
```
- Signature (서명): Base64UrlEncode(header) + "." + Base64UrlEncode(payload) 를 비밀키로 서명 => 서버가 토큰 변조 여부를 검증
```
HMACSHA256(
  base64UrlEncode(header) + "." + base64UrlEncode(payload),
  secret)
```
- jwt 용도: 인증(Authentication), 인가(Authorization), 정보전달
- jwt 주의점: JWT는 암호화가 아님, 누구나 payload 내용을 볼 수 있음 (Base64 decode 가능), 유효기간(exp) 동안 탈취된 토큰으로 무단 사용 가능 → HTTPS + 적절한 만료 + 리프레시 토큰 조합 필요

TLS (Transport Layer Security)
- TLS (Transport Layer Security): 애플리케이션 계층과 전송 계층 사이에서 데이터 통신을 암호화하는 프로토콜
- 기밀성 (Confidentiality): 데이터가 암호화되어 전송 중에 도청당해도 내용을 알 수 없음 (예: Wireshark로 캡처해도 못 봄)
- 무결성 (Integrity): 데이터가 중간에서 변조되지 않았음을 보장 (MAC, HMAC, 해시 활용)
- 인증 (Authentication): 서버 (그리고 경우에 따라 클라이언트)의 신원을 증명 (서버 인증서 기반 X.509)
- TLS Tunnel: 클라이언트와 서버 간 암호화된 터널을 형성. 이 터널을 통해 모든 기밀 데이터 (JWT, API 데이터, 개인정보 등) 송수신
- mTLS (mutual TLS): 양방향 TLS 인증. 클라이언트도 인증서를 제공 → 서버가 클라이언트 신원도 검증
- 핸드셰이크 단계(세션 키 생성): 클라이언트와 서버가 안전하게 공유 키를 만드는 과정. 비대칭 키 방식 사용
- 데이터 암호화 단계 (세션 데이터 보호): 핸드셰이크로 공유된 세션 키를 기반으로 대칭키 암호화를 사용
