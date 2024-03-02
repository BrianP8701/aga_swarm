"""
The swarm consists of nodes. Each node is given a message 
and a preassigned action they must execute.
"""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel
from typing_extensions import Literal

from swarmstar.utils.misc.uuid import generate_uuid

class SwarmNode(BaseModel):
    id: Optional[str] = generate_uuid('node')
    parent_id: Optional[str] = None
    children_ids: List[str] = []
    operation_ids: List[str] = []
    action_id: str
    message: str
    alive: bool
    termination_policy: Literal[
        "simple",
        "parallel_review",
        "clone_with_questions_answered",
    ]
    developer_logs: List[Dict[str, Any]] = []
    journal: List[Dict[str, Any]] = []
    report: Optional[str] = None
