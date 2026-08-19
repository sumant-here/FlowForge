from app.models.job import JobStatus
from app.models.workflow import WorkflowStatus
from app.core.exceptions import InvalidStateTransitionError

VALID_JOB_TRANSITIONS = {
    JobStatus.PENDING: {JobStatus.QUEUED, JobStatus.CANCELLED},
    JobStatus.QUEUED: {JobStatus.RUNNING, JobStatus.CANCELLED, JobStatus.QUEUED},
    JobStatus.RUNNING: {JobStatus.SUCCEEDED, JobStatus.FAILED, JobStatus.RETRYING, JobStatus.CANCELLED, JobStatus.QUEUED},
    JobStatus.FAILED: {JobStatus.RETRYING, JobStatus.DEAD_LETTERED, JobStatus.QUEUED},
    JobStatus.RETRYING: {JobStatus.QUEUED, JobStatus.DEAD_LETTERED, JobStatus.CANCELLED},
    JobStatus.SUCCEEDED: {JobStatus.QUEUED},
    JobStatus.CANCELLED: {JobStatus.QUEUED},
    JobStatus.DEAD_LETTERED: {JobStatus.QUEUED}
}

VALID_WORKFLOW_TRANSITIONS = {
    WorkflowStatus.DRAFT: {WorkflowStatus.RUNNING, WorkflowStatus.CANCELLED},
    WorkflowStatus.RUNNING: {WorkflowStatus.SUCCEEDED, WorkflowStatus.FAILED, WorkflowStatus.PAUSED, WorkflowStatus.CANCELLED},
    WorkflowStatus.PAUSED: {WorkflowStatus.RUNNING, WorkflowStatus.CANCELLED},
    WorkflowStatus.SUCCEEDED: {WorkflowStatus.RUNNING},
    WorkflowStatus.FAILED: {WorkflowStatus.RUNNING},
    WorkflowStatus.CANCELLED: {WorkflowStatus.RUNNING}
}

class StateMachine:
    @staticmethod
    def validate_job_transition(current_status: JobStatus, target_status: JobStatus):
        allowed = VALID_JOB_TRANSITIONS.get(current_status, set())
        if target_status not in allowed:
            raise InvalidStateTransitionError(current_status.value, target_status.value)

    @staticmethod
    def validate_workflow_transition(current_status: WorkflowStatus, target_status: WorkflowStatus):
        allowed = VALID_WORKFLOW_TRANSITIONS.get(current_status, set())
        if target_status not in allowed:
            raise InvalidStateTransitionError(current_status.value, target_status.value)