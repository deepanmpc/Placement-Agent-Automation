import time
from contextlib import contextmanager
from typing import Dict, Any

from vision_service.utils.logger import logger

class Metrics:
    def __init__(self):
        self.timings: Dict[str, float] = {}

    @contextmanager
    def measure(self, name: str):
        start = time.perf_counter()
        yield
        end = time.perf_counter()
        duration_ms = (end - start) * 1000
        self.timings[name] = duration_ms
        logger.debug(f"Timing [{name}]: {duration_ms:.2f}ms")

    def get_metrics(self) -> Dict[str, Any]:
        return self.timings

    def reset(self):
        self.timings.clear()

global_metrics = Metrics()
