from pydantic import BaseModel
from typing import Any, Dict

class ResponseTool(BaseModel):
    url: str
    method: str
    payload: Any