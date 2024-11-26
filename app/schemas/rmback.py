from pydantic import BaseModel, HttpUrl
from typing import Union, List
import datetime

# 요청 스키마
class RmbackRequest(BaseModel):
    input_url: HttpUrl

# 응답 스키마
class RmbackResponse(BaseModel):
    id: int
    input_url: HttpUrl
    output_url: Union[HttpUrl, List[HttpUrl]]
    status: str
    media_type: str
    created_at: datetime.datetime

    class Config:
        orm_mode = True
