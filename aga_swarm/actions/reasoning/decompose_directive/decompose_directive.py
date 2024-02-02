import json
from pydantic import validate_call, BaseModel, Field
import traceback
from typing import List

from aga_swarm.swarm.types import NodeOutput, SwarmConfig, SwarmCommand, LifecycleCommand, NodeOutput
from aga_swarm.utils.llm import completion

class Input(BaseModel):
    directive: str
    swarm_config: SwarmConfig
    
Output = NodeOutput    

def decompose_directive(input: Input) -> NodeOutput:
    with open('aga_swarm/actions/reasoning/decompose_directive/tool.json', 'r') as file:
        decompose_directive_blueprint = json.load(file)
    
    system_instructions = '''You must output following the specified JSON schema. You play 
    a pivotal role in navigating complex goals across various levels in domains like software 
    development, engineering, and research. Your operations within this multi-tiered system 
    include:\n\nIterative Goal Interpretation and Decomposition: In the swarm hierarchy, you'll 
    handle goals at different completion stages. Your primary task is to break down these goals 
    into smaller, actionable sub-goals. This process involves one critical pathway:\n\nDirect 
    Subgoal Generation: Based on the existing information, proceed to generate and output a list 
    of subgoals.\n\nSubgoal Contextualization and Assignment: When formulating subgoals, ensure 
    each one is bundled with all relevant and available information. Strive for a balance between 
    providing enough detail for effective downstream execution and maintaining overall resource 
    efficiency.\n\nParallel Goal Output: Focus on identifying subgoals that can be pursued 
    immediately and in parallel, independent of other tasks. Your output should exclusively 
    list these parallelizable subgoals, omitting any that are sequential or reliant on the 
    completion of others. Sequential or dependent goals will be formulated in subsequent phases 
    once the immediate parallel tasks are completed.\n\nDynamic Routing and Task Delegation: Your 
    formulated subgoals are routed to the 'router' agent. This agent is responsible for assigning 
    tasks to suitable subagents, who will execute actions like coding, further goal decomposition, 
    research and more.\n\nCost-Efficiency and Operations: Uphold cost-efficiency at every management 
    level. Ensure that the subgoals you provide are detailed yet concise, adhering to the context 
    window and budgetary constraints.'''
    
    class DecomposeDirective(BaseModel):
        subdirectives: List[str] = Field(..., description="Decompose the directive into subdirectives")
    
    messages = [
        {
            "role": "system",
            "content": system_instructions
        },
        {
            "role": "user",
            "content": f'Directive: \n`{input.directive}`'
        }
    ]
    
    try:
        subdirectives = completion(messages, input.swarm_config.configs.openai_key, DecomposeDirective, max_retries=2).subdirectives
    except Exception as e:
        return NodeOutput(
            lifecycle_command=LifecycleCommand.NODE_FAILURE,
            swarm_commands=[],
            report=str(e) + "\nTraceback:\n" + traceback.format_exc()
        )

    swarm_commands = []
    for subdirective in subdirectives:
        swarm_command = SwarmCommand(
            action_id='aga_swarm/actions/swarm/actions/route_to_action',
            params = {
                'directive': subdirective,
                'swarm_config': input.swarm_config
            }
        )
        swarm_commands.append(swarm_command)
    
    return NodeOutput(
        lifecycle_command=LifecycleCommand.SPAWN,
        swarm_commands=swarm_commands,
        report=f'Directive: {input.directive}\n\nSubdirectives:\n' + '\n'.join(subdirectives)
    )

@validate_call
def main(directive: str, swarm_config: SwarmConfig) -> NodeOutput:
    return decompose_directive(directive, swarm_config)