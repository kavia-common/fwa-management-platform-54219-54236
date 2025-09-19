from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from src.core.database import Base, engine, get_db
from src.dependencies.auth import require_admin
from src.models.models import User, Device, Telemetry

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.post("/init-db", summary="Initialize database tables")
# PUBLIC_INTERFACE
def init_db(_: User = Depends(require_admin)) -> dict:
    """Create all tables in the database based on SQLAlchemy models."""
    Base.metadata.create_all(bind=engine)
    return {"status": "ok", "message": "Database tables created"}


@router.post("/seed-admin", summary="Create initial admin user")
# PUBLIC_INTERFACE
def seed_admin(db: Session = Depends(get_db), _: User = Depends(require_admin)) -> dict:
    """Create a default admin user if none exist."""
    from src.core.security import get_password_hash
    exists = db.query(User).filter(User.is_admin == True).first()  # noqa: E712
    if exists:
        return {"status": "ok", "message": "Admin already exists"}
    admin = User(email="admin@example.com", hashed_password=get_password_hash("admin123"), is_admin=True, is_active=True)
    db.add(admin)
    db.commit()
    return {"status": "ok", "message": "Admin created", "email": admin.email}


@router.get("/stats", summary="System statistics")
# PUBLIC_INTERFACE
def system_stats(db: Session = Depends(get_db), _: User = Depends(require_admin)) -> dict:
    """Return a snapshot of system statistics."""
    users_count = db.query(func.count(User.id)).scalar() or 0
    devices_count = db.query(func.count(Device.id)).scalar() or 0
    telemetry_count = db.query(func.count(Telemetry.id)).scalar() or 0
    return {
        "users": users_count,
        "devices": devices_count,
        "telemetry": telemetry_count,
    }
