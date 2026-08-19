from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from app.models.workflow import WorkflowStatus

class WorkflowNode(BaseModel):
    id: str
    name: str
    job_type: str = "cpu_intensive"
    payload: Dict[str, Any] = Field(default_factory=dict)
    position: Optional[Dict[str, float]] = None

class WorkflowEdge(BaseModel):
    id: Optional[str] = None
    source: str
    target: str
    condition: str = "success"

class WorkflowDefinition(BaseModel):
    nodes: List[WorkflowNode]
    edges: List[WorkflowEdge]

class WorkflowCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    definition: WorkflowDefinition

class WorkflowUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    definition: Optional[WorkflowDefinition] = None

class WorkflowNodeStateResponse(BaseModel):
    id: str
    node_id: str
    job_id: Optional[str] = None
    status: str
    input_data: Dict[str, Any] = Field(default_factory=dict)
    output_data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)

class WorkflowResponse(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    status: WorkflowStatus
    definition: Dict[str, Any]
    context_data: Dict[str, Any] = Field(default_factory=dict)
    error: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration_ms: Optional[int] = None
    node_states: List[WorkflowNodeStateResponse] = []
    model_config = ConfigDict(from_attributes=True)