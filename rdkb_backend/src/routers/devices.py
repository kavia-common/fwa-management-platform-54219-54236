from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from src.core.database import get_db
from src.dependencies.auth import get_current_user
from src.models.models import Device
from src.schemas.common import DeviceCreate, DeviceUpdate, DeviceOut
from src.models.models import User

router = APIRouter(prefix="/devices", tags=["Devices"])


@router.post("", response_model=DeviceOut, summary="Register device")
# PUBLIC_INTERFACE
def create_device(payload: DeviceCreate, db: Session = Depends(get_db), _: User = Depends(get_current_user)) -> DeviceOut:
    """Register a new device."""
    exists = db.query(Device).filter(Device.serial_number == payload.serial_number).first()
    if exists:
        raise HTTPException(status_code=400, detail="Device with serial number already exists")
    device = Device(
        serial_number=payload.serial_number,
        model=payload.model,
        firmware_version=payload.firmware_version,
        owner_id=payload.owner_id,
        status="offline",
        last_seen=None,
    )
    db.add(device)
    db.commit()
    db.refresh(device)
    return _to_device_out(device)


@router.get("", response_model=List[DeviceOut], summary="List devices")
# PUBLIC_INTERFACE
def list_devices(status: str | None = Query(default=None, description="Filter by status"), db: Session = Depends(get_db), _: User = Depends(get_current_user)) -> List[DeviceOut]:
    """List all devices with optional status filter."""
    q = db.query(Device)
    if status:
        q = q.filter(Device.status == status)
    return [_to_device_out(d) for d in q.order_by(Device.created_at.desc()).all()]


@router.get("/{device_id}", response_model=DeviceOut, summary="Get device by ID")
# PUBLIC_INTERFACE
def get_device(device_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)) -> DeviceOut:
    """Get a single device by ID."""
    device = db.get(Device, device_id)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    return _to_device_out(device)


@router.put("/{device_id}", response_model=DeviceOut, summary="Update device")
# PUBLIC_INTERFACE
def update_device(device_id: int, payload: DeviceUpdate, db: Session = Depends(get_db), _: User = Depends(get_current_user)) -> DeviceOut:
    """Update a device fields."""
    device = db.get(Device, device_id)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    if payload.model is not None:
        device.model = payload.model
    if payload.firmware_version is not None:
        device.firmware_version = payload.firmware_version
    if payload.status is not None:
        device.status = payload.status
        if payload.status == "online":
            device.last_seen = datetime.utcnow()
    if payload.owner_id is not None:
        device.owner_id = payload.owner_id
    db.add(device)
    db.commit()
    db.refresh(device)
    return _to_device_out(device)


@router.delete("/{device_id}", summary="Delete device", status_code=204)
# PUBLIC_INTERFACE
def delete_device(device_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)) -> None:
    """Delete a device."""
    device = db.get(Device, device_id)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    db.delete(device)
    db.commit()
    return None


def _to_device_out(d: Device) -> DeviceOut:
    return DeviceOut(
        id=d.id,
        serial_number=d.serial_number,
        model=d.model,
        firmware_version=d.firmware_version,
        status=d.status,
        last_seen=d.last_seen,
        owner_id=d.owner_id,
        created_at=d.created_at,
    )
