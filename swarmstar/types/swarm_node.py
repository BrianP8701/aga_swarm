"""
The swarm consists of nodes. Each node is given a message 
and a preassigned action they must execute.
"""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field
from typing_extensions import Literal

from swarmstar.utils.misc.generate_uuid import generate_uuid

class SwarmNode(BaseModel):
    id: Optional[str] = Field(default_factory=lambda: generate_uuid("node"))
    name: str
    parent_id: Optional[str] = None
    children_ids: List[str] = []
    action_id: str
    message: str
    alive: bool = True
    termination_policy: Literal[
        "simple",
        "parallel_review",
        "clone_with_questions_answered",
    ]
    developer_logs: List[Any] = []
    report: Optional[str] = None
    execution_memory: Optional[Dict[str, Any]] = None
    context: Optional[Dict[str, Any]] = None
