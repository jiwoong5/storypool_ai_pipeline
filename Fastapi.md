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
