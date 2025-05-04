from pydantic import BaseModel
from datetime import datetime


class CityRequest(BaseModel):
    city: str


class AirQualityResponse(BaseModel):
    id: int
    city: str
    aqi: int | None
    pm2_5: float | None
    pm10: float | None
    co: float | None
    so2: float | None
    no2: float | None
    o3: float | None
    created_at: datetime

    class Config:
        from_attributes = True


class HealthImpactRequest(BaseModel):
    aqi: float
    pm10: float
    pm2_5: float
    no2: float
    so2: float
    o3: float


class HealthImpactResponse(BaseModel):
    health_score: float
    risk_class: str
