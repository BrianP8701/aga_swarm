from typing import List, Union

from swarmstar.swarm.types import FailureOperation, SwarmConfig, SwarmOperation
from swarmstar.swarm.decorators import swarmstar_decorator

@swarmstar_decorator
def execute_failure_operation(swarm: SwarmConfig, node_failure_operation: FailureOperation) ->  Union[SwarmOperation, List[SwarmOperation]]:
    raise NotImplementedError('Havent implemented failure handling for nodes yet.')
