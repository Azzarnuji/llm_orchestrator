from pydantic import BaseModel
import typing

class ResponseTool(BaseModel):
    url: str
    method: str
    payload: typing.Any
    additional_prompt_to_ai: typing.Optional[str] = None