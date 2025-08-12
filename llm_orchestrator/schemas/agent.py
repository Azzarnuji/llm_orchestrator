from typing import List, Optional, Literal, Dict, Any
from pydantic import BaseModel, Field


class ParameterProperty(BaseModel):
    type: str
    description: Optional[str] = None
    format: Optional[str] = None
    enum: Optional[List[str]] = None
    default: Optional[Any] = None


class Parameters(BaseModel):
    type: Literal["object"]
    properties: Dict[str, ParameterProperty]
    required: List[str]


class SchemaModel(BaseModel):
    name: str
    description: str
    parameters: Parameters


class HTTPConfig(BaseModel):
    method: Literal["GET", "POST", "PUT", "DELETE", "PATCH"]
    url: str


class Tool(BaseModel):
    name: str
    description: str
    intent_examples: List[str]
    tags: List[str]
    schema_model: SchemaModel = Field(..., alias="schema")
    http: HTTPConfig
    class Config:
        populate_by_name = True


class AgentSchema(BaseModel):
    agent_name: str
    requiredAuth: bool
    authType: Optional[str]
    tools: List[Tool]
