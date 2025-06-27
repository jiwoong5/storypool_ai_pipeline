from pydantic import BaseModel

class OCRRequest(BaseModel):
    image_data: str