from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, EmailStr


class UserCreate(BaseModel):
    email: EmailStr = Field(..., description="User email")
    password: str = Field(..., description="Plaintext password")
    is_admin: bool = Field(default=False, description="User is admin")


class UserOut(BaseModel):
    id: int = Field(..., description="User ID")
    email: EmailStr = Field(..., description="User email")
    is_active: bool = Field(..., description="Is active")
    is_admin: bool = Field(..., description="Is admin")
    created_at: datetime = Field(..., description="Creation date")


class DeviceCreate(BaseModel):
    serial_number: str = Field(..., description="Device serial number")
    model: str = Field(..., description="Device model")
    firmware_version: Optional[str] = Field(default=None, description="Firmware version")
    owner_id: Optional[int] = Field(default=None, description="Owner user ID")


class DeviceUpdate(BaseModel):
    model: Optional[str] = Field(default=None, description="Device model")
    firmware_version: Optional[str] = Field(default=None, description="Firmware version")
    status: Optional[str] = Field(default=None, description="Operational status")
    owner_id: Optional[int] = Field(default=None, description="Owner user ID")


class DeviceOut(BaseModel):
    id: int
    serial_number: str
    model: str
    firmware_version: Optional[str]
    status: str
    last_seen: Optional[datetime]
    owner_id: Optional[int]
    created_at: datetime


class ConfigUpsert(BaseModel):
    key: str = Field(..., description="Configuration key")
    value: str = Field(..., description="Configuration value")


class ConfigOut(BaseModel):
    id: int
    device_id: int
    key: str
    value: str


class TelemetryIn(BaseModel):
    metric: str = Field(..., description="Telemetry metric name")
    value: str = Field(..., description="Telemetry value")


class TelemetryOut(BaseModel):
    id: int
    device_id: int
    metric: str
    value: str
    recorded_at: datetime
