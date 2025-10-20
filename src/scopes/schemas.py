from pydantic import BaseModel


class ScopeCreate(BaseModel):
    name: str
    description:str


class ScopeAssign(BaseModel):
    scope_name: str

