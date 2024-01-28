from pydantic import validate_arguments
from typing import Dict, Any

def internal_default_swarm_action(action_id: str, params: Dict[str, Any]) -> dict:
    '''
        This action type is only used to execute actions that are defined in the swarm package itself.
        
        It simply calls the main function of the action script specified by the action_id with the params provided.
    '''    
    # Import the main function from the path specified by the action_id
    import_action_id = action_id.replace('/', '.')
    if import_action_id.endswith('.py'):
        import_action_id = import_action_id[:-3]
    action = __import__(import_action_id, fromlist=[''])
    if hasattr(action, 'main'):
        main_function = getattr(action, 'main')
    else:
        raise AttributeError("No main function found in the script")
    
    return main_function(**params)

@validate_arguments
def main(action_id: str, params: Dict[str, Any]):
    return internal_default_swarm_action(action_id, params)