"""
import pytest
from httpx import AsyncClient
from fastapi import FastAPI
from ocr_api import router  # OCR API가 정의된 파일 경로
from pathlib import Path

app = FastAPI()
app.include_router(router)

@pytest.mark.asyncio
async def test_ocr_endpoint():
    test_image_path = "sample_image.png"
    assert Path(test_image_path).exists(), "테스트 이미지가 존재하지 않습니다."

    async with AsyncClient(app=app, base_url="http://test") as ac:
        with open(test_image_path, "rb") as img_file:
            files = {"image": ("sample.png", img_file, "image/png")}
            response = await ac.post("/ocr", files=files)

    assert response.status_code == 200
    json_data = response.json()
    assert "ocr_text" in json_data or "error" in json_data
    if "ocr_text" in json_data:
        assert isinstance(json_data["ocr_text"], str)
        print("\n✅ OCR 결과:\n", json_data["ocr_text"])
    else:
        print("\n❌ OCR 실패:\n", json_data["error"])
"""
import pytest
from httpx import AsyncClient
from fastapi import FastAPI
from ocr_api import router  # OCR API가 정의된 파일 경로
from pathlib import Path

app = FastAPI()
app.include_router(router)


@pytest.mark.asyncio
async def test_ocr_endpoint():
    # 현재 디렉토리에 있는 이미지 경로
    test_image_path = "sample_image.png"  # 현재 디렉토리로 수정

    assert Path(test_image_path).exists(), "테스트 이미지가 존재하지 않습니다."

    # AsyncClient를 이용한 테스트 클라이언트 생성
    async with AsyncClient(app=app, base_url="http://test") as ac:  # FastAPI 앱 인스턴스를 전달
        with open(test_image_path, "rb") as img_file:
            files = {"image": ("sample.png", img_file, "image/png")}
            response = await ac.post("/ocr", files=files)

    assert response.status_code == 200
    json_data = response.json()
    assert "ocr_text" in json_data or "error" in json_data
    if "ocr_text" in json_data:
        assert isinstance(json_data["ocr_text"], str)
        print("\n✅ OCR 결과:\n", json_data["ocr_text"])
    else:
        print("\n❌ OCR 실패:\n", json_data["error"])
