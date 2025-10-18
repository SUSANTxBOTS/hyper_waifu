from pydantic import BaseModel
from typing import Optional
from bson import ObjectId
from datetime import datetime

# Helper to support MongoDB ObjectId in Pydantic
class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

# ---------- WAIFU MODEL ----------
class Waifu(BaseModel):
    id: Optional[PyObjectId] = None
    waifu_id: int
    name: str
    anime: str
    rarity: int
    image: str
    added_by: Optional[int] = None   # user_id who uploaded
    created_at: Optional[datetime] = None

    class Config:
        json_encoders = {ObjectId: str}

# ---------- COINS MODEL ----------
class Coins(BaseModel):
    id: Optional[PyObjectId] = None
    user_id: int
    coins: int = 0

    class Config:
        json_encoders = {ObjectId: str}