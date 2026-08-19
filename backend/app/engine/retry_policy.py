import random
import math
from app.core.exceptions import NonRetryableJobError

class RetryPolicy:
    @staticmethod
    def calculate_delay(
        attempt: int,
        strategy: str = "exponential",
        base_delay_seconds: int = 2,
        max_delay_seconds: int = 300,
        jitter: bool = True
    ) -> float:
        """Calculates backoff delay for retrying jobs with exponential, linear, or fixed delay + jitter."""
        if attempt <= 1:
            delay = base_delay_seconds
        elif strategy == "exponential":
            delay = base_delay_seconds * (2 ** (attempt - 1))
        elif strategy == "linear":
            delay = base_delay_seconds * attempt
        else: # fixed
            delay = base_delay_seconds
        
        delay = min(delay, max_delay_seconds)
        
        if jitter:
            # Full jitter: random uniform between 0 and calculated delay
            delay = random.uniform(0.5 * delay, 1.2 * delay)
            
        return round(max(0.5, delay), 2)

    @staticmethod
    def is_retryable(exception: Exception) -> bool:
        if isinstance(exception, NonRetryableJobError):
            return False
        return True
