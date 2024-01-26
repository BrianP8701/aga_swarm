from pydantic import validate_arguments

from aga_swarm.actions.swarm.action_types.internal_swarm_default_action import internal_swarm_default_action as execute
from aga_swarm.core.swarm.types import SwarmID

@validate_arguments
def main(swarm_id: SwarmID, file_path: str, data: bytes) -> dict:
    platform = swarm_id.platform
    return execute(f'aga_swarm/actions/data/file_operations/upload_file/{platform}_upload_file.py', 
                   swarm_id, {'file_path': file_path, 'data': data})
    