from io import BytesIO
import boto3, os
from dotenv import load_dotenv

# Db url 가져오기
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
BASE_URL = os.getenv("BASE_URL")
SERVICE_TOKEN = os.getenv("SERVICE_TOKEN")
NOTIFY_ENDPOINT = os.getenv("NOTIFY_ENDPOINT")

AWS_REGION = os.getenv("AWS_S3_REGION")
AWS_BUCKET = os.getenv("AWS_S3_BUCKET_NAME")
AWS_ACCESS_KEY = os.getenv("AWS_S3_ACCESS_KEY")
AWS_SECRET_KEY = os.getenv("AWS_S3_SECRET_KEY")
PRESIGNED_EXPIRATION = int(os.getenv("AWS_S3_PRESIGNED_URL_EXPIRATION", "300")) 

# 테스트용 이미지 파일 경로 (PNG 이미지)
test_image_path = "../test.png"

# 이미지 파일 읽기 (바이너리 모드)
with open(test_image_path, "rb") as f:
    image_bytes = f.read()

# S3 경로 예: "test-folder/test_upload.png"
s3_key = "test-folder/test_upload.png"

s3_client = boto3.client(
    "s3",
    region_name=AWS_REGION,
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY,
)


def upload_image_to_s3(image_bytes: bytes, s3_key: str) -> str:
    # 바이트 데이터를 스트림으로 변환
    file_obj = BytesIO(image_bytes)

    # S3에 업로드
    s3_client.upload_fileobj(
        Fileobj=file_obj,
        Bucket=AWS_BUCKET,
        Key=s3_key,
        ExtraArgs={"ContentType": "image/png"}
    )

    # presigned URL 생성 및 반환
    url = s3_client.generate_presigned_url(
        ClientMethod="get_object",
        Params={"Bucket": AWS_BUCKET, "Key": s3_key},
        ExpiresIn=PRESIGNED_EXPIRATION,
    )
    return url


# 업로드 함수 호출
url = upload_image_to_s3(image_bytes, s3_key)

print("Uploaded to S3:", url)
