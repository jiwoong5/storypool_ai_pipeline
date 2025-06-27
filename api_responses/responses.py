from pydantic import BaseModel
from typing import List, Optional

class OCRResponse(BaseModel):
    status: str
    text_list: Optional[List[str]] = None
    error_message: Optional[str] = None