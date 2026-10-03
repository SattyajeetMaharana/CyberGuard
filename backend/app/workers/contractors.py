from dataclasses import dataclass
from typing import Callable


@dataclass
class WorkerJob:
    name: str
    handler: Callable