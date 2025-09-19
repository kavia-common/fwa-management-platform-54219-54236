from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.core.database import get_db
from src.dependencies.auth import get_current_user
from src.models.models import Device, DeviceConfig, User
from src.schemas.common import ConfigUpsert, ConfigOut

router = APIRouter(prefix="/configs", tags=["Configuration"])


@router.post("/devices/{device_id}", response_model=ConfigOut, summary="Upsert device configuration")
# PUBLIC_INTERFACE
def upsert_device_config(device_id: int, payload: ConfigUpsert, db: Session = Depends(get_db), _: User = Depends(get_current_user)) -> ConfigOut:
    """Create or update a device configuration key/value."""
    device = db.get(Device, device_id)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    conf = db.query(DeviceConfig).filter(DeviceConfig.device_id == device_id, DeviceConfig.key == payload.key).first()
    if conf:
        conf.value = payload.value
    else:
        conf = DeviceConfig(device_id=device_id, key=payload.key, value=payload.value)
        db.add(conf)
    db.commit()
    db.refresh(conf)
    return ConfigOut(id=conf.id, device_id=conf.device_id, key=conf.key, value=conf.value)


@router.get("/devices/{device_id}", response_model=List[ConfigOut], summary="List device configurations")
# PUBLIC_INTERFACE
def list_device_configs(device_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)) -> List[ConfigOut]:
    """List all configuration entries for a device."""
    device = db.get(Device, device_id)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    items = db.query(DeviceConfig).filter(DeviceConfig.device_id == device_id).all()
    return [ConfigOut(id=i.id, device_id=i.device_id, key=i.key, value=i.value) for i in items]
