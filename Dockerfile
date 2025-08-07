# syntax=docker/dockerfile:1

## 1단계: 의존성 설치 전용 스테이지
ARG PYTHON_VERSION=3.12.7
FROM python:${PYTHON_VERSION}-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# requirements.txt만 먼저 복사 (의존성 캐시 최적화)
COPY requirements.txt .

# pip 캐시 활용해 의존성 설치
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --upgrade pip && \
    pip install --prefix=/install -r requirements.txt

## 2단계: 최종 실행 이미지
FROM python:${PYTHON_VERSION}-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# 앱 실행용 사용자 생성
ARG UID=10001
RUN adduser \
    --disabled-password \
    --gecos "" \
    --home "/nonexistent" \
    --shell "/sbin/nologin" \
    --no-create-home \
    --uid "${UID}" \
    appuser

# 캐시 디렉토리 생성 및 권한 부여
RUN mkdir -p /app/.cache/huggingface && chown appuser:appuser /app/.cache/huggingface

# base 스테이지에서 설치된 패키지 복사
COPY --from=base /install /usr/local

# 앱 코드 복사
COPY . .

# Hugging Face 캐시 위치 환경변수 지정
ENV HF_HOME=/app/.cache/huggingface

# 앱 실행 포트
EXPOSE 8000

USER appuser

# 앱 실행
CMD ["uvicorn", "task_queue_server:app", "--host=0.0.0.0", "--port=8000"]
