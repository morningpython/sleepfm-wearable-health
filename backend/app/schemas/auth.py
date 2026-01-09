from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    """사용자 생성 스키마"""

    email: EmailStr = Field(..., description="사용자 이메일")
    username: str = Field(..., min_length=3, max_length=100, description="사용자명")
    full_name: str | None = Field(None, max_length=255, description="전체 이름")
    password: str = Field(..., min_length=8, description="비밀번호 (최소 8자)")

    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "username": "sleepfm_user",
                "full_name": "John Doe",
                "password": "securepassword123",
            }
        }


class UserResponse(BaseModel):
    """사용자 응답 스키마"""

    id: int
    email: str
    username: str
    full_name: str | None = None
    is_active: bool

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "email": "user@example.com",
                "username": "sleepfm_user",
                "full_name": "John Doe",
                "is_active": True,
            }
        }


class UserLogin(BaseModel):
    """로그인 스키마"""

    email: EmailStr = Field(..., description="사용자 이메일")
    password: str = Field(..., description="비밀번호")

    class Config:
        json_schema_extra = {
            "example": {"email": "user@example.com", "password": "securepassword123"}
        }


class Token(BaseModel):
    """토큰 응답 스키마"""

    access_token: str = Field(..., description="접근 토큰")
    refresh_token: str = Field(..., description="갱신 토큰")
    token_type: str = Field(default="bearer", description="토큰 타입")
    expires_in: int = Field(..., description="만료 시간 (초)")

    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "expires_in": 900,
            }
        }


class TokenRefresh(BaseModel):
    """토큰 갱신 스키마"""

    refresh_token: str = Field(..., description="갱신 토큰")

    class Config:
        json_schema_extra = {
            "example": {"refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."}
        }
