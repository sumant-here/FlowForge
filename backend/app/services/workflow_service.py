import uuid
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.exceptions import FlowForgeException
from app.engine.dag_engine import DAGEngine
from app.engine.state_machine import StateMachine
from app.models.workflow import Workflow, WorkflowStatus, WorkflowNodeState
from app.models.job import JobPriority
from app.schemas.workflow import WorkflowCreate
from app.schemas.job import JobCreate
from app.repositories.workflow_repo import WorkflowRepository
from app.services.job_service import JobService

class WorkflowService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.workflow_repo = WorkflowRepository(db)
        self.job_service = JobService(db)

    async def create_workflow(self, data: WorkflowCreate) -> Workflow:
        def_dict = data.definition.model_dump()
        DAGEngine.validate_and_sort(def_dict)

        wf = Workflow(
            id=str(uuid.uuid4()),
            name=data.name,
            description=data.description,
            status=WorkflowStatus.DRAFT,
            definition=def_dict,
            context_data={},
            created_at=datetime.now(timezone.utc)
        )
        return await self.workflow_repo.create(wf)

    async def run_workflow(self, workflow_id: str, input_context: Optional[Dict[str, Any]] = None) -> Workflow:
        wf = await self.workflow_repo.get_detail(workflow_id)
        if not wf:
            raise FlowForgeException("Workflow not found", status_code=404)

        StateMachine.validate_workflow_transition(wf.status, WorkflowStatus.RUNNING)
        wf.status = WorkflowStatus.RUNNING
        wf.started_at = datetime.now(timezone.utc)
        wf.completed_at = None
        wf.error = None
        if input_context:
            wf.context_data = input_context
        
        await self.db.commit()

        layers = DAGEngine.validate_and_sort(wf.definition)
        first_layer_node_ids = layers[0] if layers else []
        nodes_map = {n["id"]: n for n in wf.definition.get("nodes", [])}

        for nid in first_layer_node_ids:
            node_def = nodes_map.get(nid, {})
            job_in = JobCreate(
                name=f"{wf.name} - {node_def.get('name', nid)}",
                job_type=node_def.get("job_type", "cpu_intensive"),
                priority=JobPriority.HIGH,
                payload={**node_def.get("payload", {}), **wf.context_data}
            )
            created_job = await self.job_service.submit_job(job_in, workflow_id=wf.id, node_id=nid)

            node_state = WorkflowNodeState(
                id=str(uuid.uuid4()),
                workflow_id=wf.id,
                node_id=nid,
                job_id=created_job.id,
                status="RUNNING",
                input_data=job_in.payload,
                started_at=datetime.now(timezone.utc)
            )
            await self.workflow_repo.save_node_state(node_state)

        await self.db.refresh(wf)
        return wf

    async def handle_job_completed(self, workflow_id: str, node_id: str, status: str, output_data: Dict[str, Any], error: Optional[str] = None):
        wf = await self.workflow_repo.get_detail(workflow_id)
        if not wf or wf.status != WorkflowStatus.RUNNING:
            return

        for ns in wf.node_states:
            if ns.node_id == node_id:
                ns.status = status
                ns.output_data = output_data
                ns.error = error
                ns.completed_at = datetime.now(timezone.utc)
                break

        merged_context = dict(wf.context_data or {})
        merged_context[node_id] = output_data
        wf.context_data = merged_context

        completed_map = {
            ns.node_id: {"status": ns.status, "output": ns.output_data}
            for ns in wf.node_states
            if ns.status in ("SUCCEEDED", "FAILED")
        }

        if status == "FAILED":
            wf.status = WorkflowStatus.FAILED
            wf.error = f"Step '{node_id}' failed: {error}"
            wf.completed_at = datetime.now(timezone.utc)
            if wf.started_at:
                wf.duration_ms = int((wf.completed_at - wf.started_at).total_seconds() * 1000)
            await self.db.commit()
            return

        ready_nodes = DAGEngine.get_ready_nodes(wf.definition, completed_map)
        nodes_map = {n["id"]: n for n in wf.definition.get("nodes", [])}

        if ready_nodes:
            for nid in ready_nodes:
                node_def = nodes_map.get(nid, {})
                job_in = JobCreate(
                    name=f"{wf.name} - {node_def.get('name', nid)}",
                    job_type=node_def.get("job_type", "cpu_intensive"),
                    priority=JobPriority.HIGH,
                    payload={**node_def.get("payload", {}), **wf.context_data}
                )
                created_job = await self.job_service.submit_job(job_in, workflow_id=wf.id, node_id=nid)

                node_state = WorkflowNodeState(
                    id=str(uuid.uuid4()),
                    workflow_id=wf.id,
                    node_id=nid,
                    job_id=created_job.id,
                    status="RUNNING",
                    input_data=job_in.payload,
                    started_at=datetime.now(timezone.utc)
                )
                await self.workflow_repo.save_node_state(node_state)
        else:
            total_nodes = len(wf.definition.get("nodes", []))
            if len(completed_map) >= total_nodes:
                wf.status = WorkflowStatus.SUCCEEDED
                wf.completed_at = datetime.now(timezone.utc)
                if wf.started_at:
                    wf.duration_ms = int((wf.completed_at - wf.started_at).total_seconds() * 1000)

        await self.db.commit()
