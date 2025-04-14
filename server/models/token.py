from sqlalchemy import Column, Integer, String, DateTime
from core.database import Base

class TokenBlacklist(Base):
    __tablename__ = "token_blacklist"

    id = Column(Integer, primary_key=True, index=True)
    token = Column(String, unique=True, index=True)
    blacklisted_at = Column(DateTime)
    expires_at = Column(DateTime)

    class Config:
        orm_mode = True 