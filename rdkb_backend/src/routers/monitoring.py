from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from src.core.database import get_db
from src.dependencies.auth import get_current_user
from src.models.models import Telemetry, Device, User
from src.schemas.common import TelemetryIn, TelemetryOut

router = APIRouter(prefix="/monitoring", tags=["Monitoring"])


@router.post("/devices/{device_id}/telemetry", response_model=TelemetryOut, summary="Submit telemetry")
# PUBLIC_INTERFACE
def submit_telemetry(device_id: int, payload: TelemetryIn, db: Session = Depends(get_db), _: User = Depends(get_current_user)) -> TelemetryOut:
    """Submit a telemetry datapoint for a device."""
    device = db.get(Device, device_id)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    t = Telemetry(device_id=device_id, metric=payload.metric, value=payload.value)
    db.add(t)
    db.commit()
    db.refresh(t)
    return TelemetryOut(id=t.id, device_id=t.device_id, metric=t.metric, value=t.value, recorded_at=t.recorded_at)


@router.get("/devices/{device_id}/telemetry", response_model=List[TelemetryOut], summary="List telemetry")
# PUBLIC_INTERFACE
def list_telemetry(
    device_id: int,
    metric: Optional[str] = Query(default=None, description="Filter by metric name"),
    limit: int = Query(default=100, le=1000, description="Max items"),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
) -> List[TelemetryOut]:
    """List telemetry datapoints for a device with optional metric filtering."""
    device = db.get(Device, device_id)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    q = db.query(Telemetry).filter(Telemetry.device_id == device_id)
    if metric:
        q = q.filter(Telemetry.metric == metric)
    q = q.order_by(Telemetry.recorded_at.desc()).limit(limit)
    items = q.all()
    return [TelemetryOut(id=i.id, device_id=i.device_id, metric=i.metric, value=i.value, recorded_at=i.recorded_at) for i in items]
