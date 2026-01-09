from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    """헬스 체크 응답"""

    status: str = Field(..., description="서비스 상태")
    service: str = Field(..., description="서비스명")
    version: str = Field(..., description="API 버전")

    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "service": "SleepFM Backend API",
                "version": "0.1.0",
            }
        }


class ErrorResponse(BaseModel):
    """에러 응답"""

    detail: str = Field(..., description="에러 상세 메시지")
    message: str = Field(..., description="에러 메시지")

    class Config:
        json_schema_extra = {
            "example": {
                "detail": "예상치 못한 에러",
                "message": "내부 서버 에러가 발생했습니다",
            }
        }


class ValidationErrorResponse(BaseModel):
    """검증 에러 응답"""

    detail: list = Field(..., description="검증 에러 목록")
    message: str = Field(..., description="에러 메시지")

    class Config:
        json_schema_extra = {
            "example": {
                "detail": [
                    {
                        "loc": ["body", "field_name"],
                        "msg": "field required",
                        "type": "value_error.missing",
                    }
                ],
                "message": "요청 데이터가 유효하지 않습니다",
            }
        }
