## 파일 클래스
UploadFile
- FastAPI에서 파일 업로드를 받을 때 사용하는 타입
- 클라이언트가 업로드한 파일을 메모리 또는 임시 파일로 관리하며, 파일 이름, 콘텐츠 타입, 스트림 객체 등을 제공
- 클래스: starlette.datastructures.UploadFile

UploadFile 주요속성
- filename: 업로드된 파일의 이름 (예: "image.png")
- content_type: MIME 타입 (예: "image/png", "text/plain")
- file: SpooledTemporaryFile 객체 (스트림으로 읽거나 쓸 수 있음)

MIME(Multipurpose Internet Mail Extensions type)
- 파일의 형식(콘텐츠의 종류) 을 인터넷에서 주고받을 때 명시하는 표준 문자열. 주타입/서브타입으로 구성
<div align="center">

| MIME 타입            | 의미         |
|----------------------|--------------|
| `text/plain`          | 일반 텍스트  |
| `text/html`           | HTML 문서    |
| `application/json`    | JSON 데이터  |
| `image/png`           | PNG 이미지   |
| `image/jpeg`          | JPEG 이미지  |
| `application/pdf`     | PDF 파일     |

</div>

UploadFile 메소드
```python
await file.read()        # 파일 전체 내용을 바이트로 읽음
await file.write(data)   # 파일에 데이터 기록 (거의 사용 X)
await file.seek(offset)  # 파일 포인터 이동
await file.close()       # 파일 닫기
```

File(...)
- file:UploadFile = File(...) 와 같이 사용
- File은 UploadFile의 생성자인가? => x
- FastAPI 엔드포인트 파라미터에 대한 선언
- FastAPI의 의존성 주입 도구로, 파일 업로드 데이터를 UploadFile 타입으로 주입해주는 역할
- file 을 업로드된 파일을 fastapi 로직으로 UploadFile 형태로 파싱해 초기화
  
UploadFile vs bytes
- UploadFile: 파일을 디스크의 임시 파일 또는 메모리 + 디스크 혼합에 저장. 스트림 형태로 데이터를 조금씩 읽음
- bytes: 요청 본문 전체를 메모리에 바이트 배열로 로드
- FastAPI 공식 문서나 Starlette 권장 사항: 메모리 전체 로드는 1MB 정도까지는 괜찮지만, 그 이상은 UploadFile(스트림)로 처리하라고 권장

<h2>Response</h2>

<table style="width:100%; table-layout: fixed; border-collapse: collapse;" border="1">
  <colgroup>
    <col style="width: 25%;">
    <col style="width: 50%;">
    <col style="width: 25%;">
  </colgroup>
  <thead>
    <tr>
      <th>클래스 / 키워드</th>
      <th>설명</th>
      <th>주요 사용 예</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><code>Response</code></td>
      <td>Base 응답 클래스 (content-type, body, header 직접 제어)</td>
      <td>HTML, plain text, 커스텀 content-type 응답</td>
    </tr>
    <tr>
      <td><code>JSONResponse</code></td>
      <td>JSON 형태 응답 (<code>application/json</code>)</td>
      <td>표준 JSON API 응답</td>
    </tr>
    <tr>
      <td><code>HTMLResponse</code></td>
      <td>HTML 응답</td>
      <td>HTML 페이지 리턴</td>
    </tr>
    <tr>
      <td><code>PlainTextResponse</code></td>
      <td><code>text/plain</code> 응답</td>
      <td>단순 텍스트 반환</td>
    </tr>
    <tr>
      <td><code>RedirectResponse</code></td>
      <td>리다이렉트 응답</td>
      <td>URL 리다이렉트</td>
    </tr>
    <tr>
      <td><code>StreamingResponse</code></td>
      <td>large file, generator 스트리밍 응답</td>
      <td>파일 다운로드, 대용량 데이터 전송</td>
    </tr>
    <tr>
      <td><code>FileResponse</code></td>
      <td>파일 다운로드 응답</td>
      <td>파일 제공</td>
    </tr>
    <tr>
      <td><code>ORJSONResponse</code></td>
      <td><code>orjson</code> 기반 고속 JSON 응답</td>
      <td>고성능 JSON serialization 필요 시</td>
    </tr>
    <tr>
      <td><code>UJSONResponse</code></td>
      <td><code>ujson</code> 기반 고속 JSON 응답</td>
      <td>(FastAPI 최신 버전에서는 거의 <code>orjson</code> 선호됨)</td>
    </tr>
    <tr>
      <td><code>status_code</code></td>
      <td>응답 상태 코드 지정</td>
      <td><code>@app.get(..., status_code=201)</code></td>
    </tr>
  </tbody>
</table>

<h2>Exception</h2>

<table style="width:100%; table-layout: fixed; border-collapse: collapse;" border="1">
  <colgroup>
    <col style="width: 25%;">
    <col style="width: 50%;">
    <col style="width: 25%;">
  </colgroup>
  <thead>
    <tr>
      <th>클래스 / 키워드</th>
      <th>설명</th>
      <th>주요 사용 예시 / 용도</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><code>HTTPException</code></td>
      <td>HTTP 상태 코드와 상세 메시지를 포함하는 예외</td>
      <td><code>raise HTTPException(status_code=404, detail="Not Found")</code></td>
    </tr>
    <tr>
      <td><code>RequestValidationError</code></td>
      <td>요청 데이터 유효성 검사 실패 시 발생하는 예외</td>
      <td>FastAPI가 자동 발생, 커스텀 핸들러 등록 가능</td>
    </tr>
    <tr>
      <td><code>ValidationError</code></td>
      <td>Pydantic 데이터 모델 검증 실패 시 발생하는 예외</td>
      <td>내부적으로 사용, 직접 처리 가능</td>
    </tr>
    <tr>
      <td><code>ExceptionHandler</code></td>
      <td>사용자 정의 예외 처리 함수 등록 시 사용하는 데코레이터</td>
      <td><code>@app.exception_handler(ExceptionType)</code></td>
    </tr>
    <tr>
      <td><code>app.exception_handler</code> 데코레이터</td>
      <td>특정 예외 타입에 대해 커스텀 예외 처리기 등록</td>
      <td><code>@app.exception_handler(HTTPException)</code></td>
    </tr>
    <tr>
      <td><code>CustomException</code></td>
      <td>직접 정의하는 사용자 예외 클래스</td>
      <td>도메인 별 의미 있는 예외 표현</td>
    </tr>
    <tr>
      <td><code>starlette.exceptions.HTTPException</code></td>
      <td>FastAPI의 HTTPException 기반 클래스 (Starlette 확장)</td>
      <td>FastAPI와 Starlette의 예외 호환성</td>
    </tr>
  </tbody>
</table>

<h2>데코레이터/파라미터</h2>

<table style="width:100%; table-layout: fixed; border-collapse: collapse;" border="1">
  <colgroup>
    <col style="width: 40%;">
    <col style="width: 60%;">
  </colgroup>
  <thead>
    <tr>
      <th>데코레이터 / 파라미터</th>
      <th>설명</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><code>@app.exception_handler(ExceptionType)</code></td>
      <td>특정 예외에 대한 커스텀 처리기 등록</td>
    </tr>
    <tr>
      <td><code>response_model</code></td>
      <td>경로 함수 응답 모델 지정 (자동 문서화 및 데이터 검증)</td>
    </tr>
    <tr>
      <td><code>responses</code></td>
      <td>상태 코드별 응답 예시 및 스키마를 OpenAPI에 추가</td>
    </tr>
    <tr>
      <td><code>status_code</code></td>
      <td>기본 응답 HTTP 상태 코드 지정</td>
    </tr>
    <tr>
      <td><code>response_class</code></td>
      <td>라우트에서 사용할 응답 클래스 지정 (<code>JSONResponse</code> 등)</td>
    </tr>
  </tbody>
</table>
