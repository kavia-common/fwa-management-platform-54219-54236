from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint, Index
from sqlalchemy.orm import relationship, Mapped, mapped_column

from src.core.database import Base


class User(Base):
    """User model for authentication and roles."""
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    devices: Mapped[list["Device"]] = relationship("Device", back_populates="owner", lazy="selectin")


class Device(Base):
    """Device model representing FWA devices managed in RDK-B."""
    __tablename__ = "devices"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    serial_number: Mapped[str] = mapped_column(String(128), unique=True, index=True, nullable=False)
    model: Mapped[str] = mapped_column(String(128), nullable=False)
    firmware_version: Mapped[str] = mapped_column(String(128), nullable=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="offline")
    last_seen: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    owner_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    owner: Mapped[Optional["User"]] = relationship("User", back_populates="devices")
    configs: Mapped[list["DeviceConfig"]] = relationship("DeviceConfig", back_populates="device", lazy="selectin")
    telemetry: Mapped[list["Telemetry"]] = relationship("Telemetry", back_populates="device", lazy="selectin")

    __table_args__ = (
        Index("ix_devices_status", "status"),
    )


class DeviceConfig(Base):
    """Configuration entries per device. Could map to RDK-B core services settings."""
    __tablename__ = "device_configs"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    device_id: Mapped[int] = mapped_column(ForeignKey("devices.id"), index=True, nullable=False)
    key: Mapped[str] = mapped_column(String(128), nullable=False)
    value: Mapped[str] = mapped_column(Text, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    device: Mapped["Device"] = relationship("Device", back_populates="configs")

    __table_args__ = (
        UniqueConstraint("device_id", "key", name="uq_device_config_key"),
        Index("ix_device_configs_key", "key"),
    )


class Telemetry(Base):
    """Monitoring telemetry data points for devices."""
    __tablename__ = "telemetry"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    device_id: Mapped[int] = mapped_column(ForeignKey("devices.id"), index=True, nullable=False)
    metric: Mapped[str] = mapped_column(String(128), index=True, nullable=False)
    value: Mapped[str] = mapped_column(String(256), nullable=False)
    recorded_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    device: Mapped["Device"] = relationship("Device", back_populates="telemetry")
