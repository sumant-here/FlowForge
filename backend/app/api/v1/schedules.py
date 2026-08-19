from typing import List
from datetime import datetime, timezone, timedelta
from croniter import croniter
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.models.schedule import Schedule
from app.schemas.schedule import ScheduleCreate, ScheduleUpdate, ScheduleResponse
from app.repositories.schedule_repo import ScheduleRepository

router = APIRouter(prefix="/schedules", tags=["Schedules"])

@router.post("", response_model=ScheduleResponse)
async def create_schedule(data: ScheduleCreate, db: AsyncSession = Depends(get_db)):
    repo = ScheduleRepository(db)
    now = datetime.now(timezone.utc)
    next_run = None
    if data.cron_expression:
        itr = croniter(data.cron_expression, now)
        next_run = itr.get_next(datetime)
    elif data.interval_seconds:
        next_run = now + timedelta(seconds=data.interval_seconds)

    s = Schedule(
        name=data.name,
        cron_expression=data.cron_expression,
        interval_seconds=data.interval_seconds,
        job_type=data.job_type,
        priority=data.priority,
        payload=data.payload,
        is_active=data.is_active,
        next_run_at=next_run
    )
    saved = await repo.create(s)
    return ScheduleResponse.model_validate(saved)

@router.get("", response_model=List[ScheduleResponse])
async def list_schedules(db: AsyncSession = Depends(get_db)):
    repo = ScheduleRepository(db)
    schedules = await repo.list(skip=0, limit=100)
    return [ScheduleResponse.model_validate(s) for s in schedules]

@router.patch("/{schedule_id}/toggle", response_model=ScheduleResponse)
async def toggle_schedule(schedule_id: str, db: AsyncSession = Depends(get_db)):
    repo = ScheduleRepository(db)
    s = await repo.get(schedule_id)
    if not s:
        raise HTTPException(status_code=404, detail="Schedule not found")
    s.is_active = not s.is_active
    await db.commit()
    await db.refresh(s)
    return ScheduleResponse.model_validate(s)
