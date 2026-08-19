class FlowForgeException(Exception):
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

class JobExecutionError(FlowForgeException):
    def __init__(self, message: str, retryable: bool = True):
        super().__init__(message, status_code=500)
        self.retryable = retryable

class NonRetryableJobError(FlowForgeException):
    def __init__(self, message: str):
        super().__init__(message, status_code=500)
        self.retryable = False

class InvalidStateTransitionError(FlowForgeException):
    def __init__(self, from_state: str, to_state: str):
        super().__init__(f"Invalid state transition: {from_state} -> {to_state}", status_code=409)

class WorkflowCyclicError(FlowForgeException):
    def __init__(self, cycle_nodes: list):
        super().__init__(f"Cyclic dependency detected: {cycle_nodes}", status_code=422)
