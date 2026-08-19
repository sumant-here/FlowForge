import pytest
from app.engine.dag_engine import DAGEngine
from app.core.exceptions import WorkflowCyclicError
from app.core.database import AsyncSessionLocal
from app.services.workflow_service import WorkflowService
from app.schemas.workflow import WorkflowCreate, WorkflowDefinition, WorkflowNode, WorkflowEdge
from app.models.workflow import WorkflowStatus

def test_dag_cycle_detection():
    cyclic_def = {
        "nodes": [{"id": "A"}, {"id": "B"}, {"id": "C"}],
        "edges": [
            {"source": "A", "target": "B"},
            {"source": "B", "target": "C"},
            {"source": "C", "target": "A"}
        ]
    }
    with pytest.raises(WorkflowCyclicError):
        DAGEngine.validate_and_sort(cyclic_def)

def test_dag_parallel_layers():
    diamond_def = {
        "nodes": [{"id": "A"}, {"id": "B"}, {"id": "C"}, {"id": "D"}],
        "edges": [
            {"source": "A", "target": "B"},
            {"source": "A", "target": "C"},
            {"source": "B", "target": "D"},
            {"source": "C", "target": "D"}
        ]
    }
    layers = DAGEngine.validate_and_sort(diamond_def)
    assert len(layers) == 3
    assert layers[0] == ["A"]
    assert set(layers[1]) == {"B", "C"}
    assert layers[2] == ["D"]

@pytest.mark.asyncio
async def test_workflow_creation_and_run():
    async with AsyncSessionLocal() as session:
        wf_service = WorkflowService(session)
        
        definition = WorkflowDefinition(
            nodes=[
                WorkflowNode(id="step1", name="Step 1", job_type="io_simulation", payload={"chunks": 1}),
                WorkflowNode(id="step2", name="Step 2", job_type="data_processing", payload={"records_count": 10})
            ],
            edges=[
                WorkflowEdge(source="step1", target="step2", condition="success")
            ]
        )
        wf = await wf_service.create_workflow(WorkflowCreate(
            name="Sequential Test Workflow",
            definition=definition
        ))
        assert wf.id is not None
        assert wf.status == WorkflowStatus.DRAFT

        # Run workflow
        running_wf = await wf_service.run_workflow(wf.id)
        assert running_wf.status == WorkflowStatus.RUNNING
        
        fetched = await wf_service.workflow_repo.get_detail(wf.id)
        assert len(fetched.node_states) == 1