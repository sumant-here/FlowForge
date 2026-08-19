from typing import Dict, Any
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.schemas.chaos import ChaosActionRequest, ChaosSimulationStatus
from app.services.chaos_service import ChaosService
from app.websocket.event_publisher import event_publisher

router = APIRouter(prefix="/chaos", tags=["Chaos Engineering Lab"])

@router.post("/execute", response_model=Dict[str, Any])
async def execute_chaos_action(req: ChaosActionRequest, db: AsyncSession = Depends(get_db)):
    service = ChaosService(db)
    result = await service.execute_chaos(req.action, req.model_dump())
    await event_publisher.publish("CHAOS_EXPERIMENT_TRIGGERED", result)
    return result
