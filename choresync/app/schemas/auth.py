"""인증 관련 Pydantic 스키마"""

from typing import Literal

from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6, max_length=100)
    name: str = Field(min_length=1, max_length=100)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


FamilyPackType = Literal["공통", "1인", "2인", "3인_영유아", "3인_초등", "3인_중고등", "4인"]


class CreateFamilyRequest(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    family_role: str = Field(default="기타", max_length=20)
    family_pack: FamilyPackType = Field(
        default="공통",
        description="할일 템플릿 팩: 공통/1인/2인/3인_영유아/3인_초등/3인_중고등/4인",
    )


class JoinFamilyRequest(BaseModel):
    invite_code: str
    family_role: str = Field(default="기타", max_length=20)
    age: int | None = None
