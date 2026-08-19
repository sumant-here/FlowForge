from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.schemas.workflow import WorkflowCreate, WorkflowResponse
from app.services.workflow_service import WorkflowService
from app.websocket.event_publisher import event_publisher

router = APIRouter(prefix="/workflows", tags=["Workflows"])

@router.post("", response_model=WorkflowResponse)
async def create_workflow(data: WorkflowCreate, db: AsyncSession = Depends(get_db)):
    service = WorkflowService(db)
    wf = await service.create_workflow(data)
    return WorkflowResponse.model_validate(wf)

@router.get("", response_model=List[WorkflowResponse])
async def list_workflows(db: AsyncSession = Depends(get_db)):
    service = WorkflowService(db)
    workflows = await service.workflow_repo.list_all()
    return [WorkflowResponse.model_validate(wf) for wf in workflows]

@router.get("/{workflow_id}", response_model=WorkflowResponse)
async def get_workflow(workflow_id: str, db: AsyncSession = Depends(get_db)):
    service = WorkflowService(db)
    wf = await service.workflow_repo.get_detail(workflow_id)
    if not wf:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return WorkflowResponse.model_validate(wf)

@router.post("/{workflow_id}/run", response_model=WorkflowResponse)
async def run_workflow(workflow_id: str, payload: Optional[Dict[str, Any]] = None, db: AsyncSession = Depends(get_db)):
    service = WorkflowService(db)
    wf = await service.run_workflow(workflow_id, input_context=payload or {})
    await event_publisher.publish("WORKFLOW_STARTED", {"workflow_id": wf.id, "name": wf.name})
    return WorkflowResponse.model_validate(wf)
