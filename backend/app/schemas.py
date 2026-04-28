from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)
    name: str = Field(min_length=1, max_length=255)


class UserPublic(BaseModel):
    id: int
    email: str
    name: str
    created_at: datetime
    email_verified: bool

    model_config = {"from_attributes": True}


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    sub: str | None = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class DenunciaCreate(BaseModel):
    title: str = Field(min_length=3, max_length=500)
    description: str = Field(min_length=10)
    violation_type: str = Field(min_length=1, max_length=100)
    empresa: str | None = Field(None, max_length=255)
    occurred_at: datetime | None = None
    location_text: str | None = Field(None, max_length=500)
    latitude: float | None = None
    longitude: float | None = None


class DenunciaPublic(BaseModel):
    id: int
    user_id: int | None
    title: str
    description: str
    violation_type: str
    empresa: str | None
    occurred_at: datetime | None
    location_text: str | None
    latitude: float | None
    longitude: float | None
    created_at: datetime

    model_config = {"from_attributes": True}
