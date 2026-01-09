from datetime import datetime

from pydantic import BaseModel, Field


class SensorData(BaseModel):
    """센서 데이터 포인트"""

    timestamp: float = Field(..., description="Unix 타임스탬프")
    heart_rate: float | None = Field(None, description="심박수 (bpm)")
    respiratory_rate: float | None = Field(None, description="호흡률 (breath/min)")
    spo2: float | None = Field(None, description="혈산소포화도 (%)")
    acceleration_x: float | None = Field(None, description="X축 가속도")
    acceleration_y: float | None = Field(None, description="Y축 가속도")
    acceleration_z: float | None = Field(None, description="Z축 가속도")

    class Config:
        json_schema_extra = {
            "example": {
                "timestamp": 1704729600.0,
                "heart_rate": 72.5,
                "respiratory_rate": 16.0,
                "spo2": 98.0,
                "acceleration_x": 0.1,
                "acceleration_y": 0.2,
                "acceleration_z": 9.8,
            }
        }


class SensorDataUpload(BaseModel):
    """센서 데이터 업로드 요청"""

    session_date: datetime = Field(..., description="수면 세션 시작 시간")
    duration_hours: int = Field(..., gt=0, le=24, description="수면 시간 (1-24시간)")
    device_type: str = Field(..., description="기기 유형 (apple_watch, galaxy_watch 등)")
    sampling_rate: int = Field(default=100, description="샘플링 레이트 (Hz)")
    data: list[SensorData] = Field(..., description="센서 데이터 배열")

    class Config:
        json_schema_extra = {
            "example": {
                "session_date": "2026-01-08T22:00:00Z",
                "duration_hours": 8,
                "device_type": "apple_watch",
                "sampling_rate": 100,
                "data": [
                    {
                        "timestamp": 1704729600.0,
                        "heart_rate": 72.5,
                        "respiratory_rate": 16.0,
                        "spo2": 98.0,
                        "acceleration_x": 0.1,
                        "acceleration_y": 0.2,
                        "acceleration_z": 9.8,
                    }
                ],
            }
        }


class SleepSessionResponse(BaseModel):
    """수면 세션 응답"""

    id: int = Field(..., description="세션 ID")
    user_id: int = Field(..., description="사용자 ID")
    session_date: datetime = Field(..., description="세션 시작 시간")
    duration_hours: int = Field(..., description="수면 시간")
    analysis_status: str = Field(..., description="분석 상태")
    raw_data_path: str | None = Field(None, description="원본 데이터 경로")
    created_at: datetime = Field(..., description="생성 시간")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "user_id": 1,
                "session_date": "2026-01-08T22:00:00Z",
                "duration_hours": 8,
                "analysis_status": "pending",
                "raw_data_path": "s3://sleepfm-data/sessions/1/20260108_220000.json",
                "created_at": "2026-01-08T22:00:00Z",
            }
        }
