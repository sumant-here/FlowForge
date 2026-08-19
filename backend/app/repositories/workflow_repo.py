from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import desc
from sqlalchemy.orm import selectinload
from app.models.workflow import Workflow, WorkflowNodeState
from app.repositories.base import BaseRepository

class WorkflowRepository(BaseRepository[Workflow]):
    def __init__(self, db: AsyncSession):
        super().__init__(Workflow, db)

    async def get_detail(self, workflow_id: str) -> Optional[Workflow]:
        query = (
            select(Workflow)
            .options(selectinload(Workflow.node_states))
            .where(Workflow.id == workflow_id)
        )
        result = await self.db.execute(query)
        return result.scalars().first()

    async def list_all(self, skip: int = 0, limit: int = 50) -> List[Workflow]:
        query = (
            select(Workflow)
            .options(selectinload(Workflow.node_states))
            .order_by(desc(Workflow.created_at))
            .offset(skip)
            .limit(limit)
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def save_node_state(self, node_state: WorkflowNodeState) -> WorkflowNodeState:
        self.db.add(node_state)
        await self.db.commit()
        await self.db.refresh(node_state)
        return node_state
