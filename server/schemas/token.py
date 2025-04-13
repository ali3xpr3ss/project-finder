from typing import Optional
from pydantic import BaseModel

class Token(BaseModel):
    access_token: str
    token_type: str
    refresh_token: Optional[str] = None

class TokenPayload(BaseModel):
    email: str

class TokenData(BaseModel):
    email: Optional[str] = None
    token_type: Optional[str] = None 