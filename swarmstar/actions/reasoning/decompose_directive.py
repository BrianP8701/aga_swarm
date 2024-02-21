'''
Decompose a directive into actionable subdirectives.

The agent will ask questions if it needs more information before decomposing the directive.
'''

from pydantic import BaseModel, Field
from typing import List, Optional

from swarmstar.swarm.types import NodeEmbryo, BlockingOperation, SpawnOperation
from swarmstar.swarm.types.base_action import BaseAction


class DecomposeDirectiveModel(BaseModel):
    scrap_paper: Optional[str] = Field(None, description='Scrap paper for notes, planning etc. Use this space to think step by step. (optional)')
    questions: Optional[List[str]] = Field(..., description="Questions you need answered before decomposition.")
    subdirectives: Optional[List[str]] = Field(..., description="List of subdirectives to be executed in parallel, if you have no questions.")

system_instructions = (
    'You are given a directive. You have 2 options:\n'
    '1. Ask questions to get more information or clarification of requirements and intentions.\n'
    '2. Decompose the directive into actionable subdirectives that will be executed independently and in parralel. '
    'After those are done, youll generate the next set of subdirectives. I stress that the subdirectives '
    'must be independent and parallel.\n\nChoose one of the options and proceed. Do not ask questions and decompose the directive at the same time.'
    )

class DecomposeDirective(BaseAction):
    def main(self) -> BlockingOperation:
        messages = [
            {
                "role": "system",
                "content": system_instructions
            },
            {
                "role": "user",
                "content": f'Directive to decompose: \n`{self.node.message}`'
            }
        ]
        
        self.add_journal_entry(
            {
                "type": "instructor_completion_request",
                "messages": messages,
                "instructor_model_name": "DecomposeDirectiveModel"
            }
        )

        return BlockingOperation(
            node_id=self.node.node_id,
            blocking_type="instructor_completion",
            args={
                "messages": messages,
                "instructor_model_name": "DecomposeDirectiveModel"
            },
            context={},
            next_function_to_call="analyze_output"
        )
    
    def analyze_output(self, completion: DecomposeDirectiveModel) -> SpawnOperation:
        if completion.questions and len(completion.questions) > 0:
            message = f'An agent was tasked with decomposing the directive: \n`{self.node.message}`\n\nBefore decomposing, the agent decided it needs the following questions answered first:\n'
            message += '\n'.join(completion.questions)
            
            self.add_journal_entry(
                {
                    "type": "question_request",
                    "message": message
                }
            )
            
            spawn_operation = SpawnOperation(
                node_id=self.node.node_id,
                node_embryo=NodeEmbryo(
                    action_id='swarmstar/actions/communication/ask_user_questions',
                    message=message
                )
            )
            return spawn_operation
        else:
            subdirectives = completion.subdirectives
            spawn_operations = []
            for subdirective in subdirectives:
                spawn_operation = SpawnOperation(
                    node_id=self.node.node_id,
                    node_embryo=NodeEmbryo(
                        action_id='swarmstar/actions/reasoning/decompose_directive',
                        message=subdirective
                    )
                )
                spawn_operations.append(spawn_operation)
            
            self.add_journal_entry(
                {
                    "type": "successfully_decomposed_directive",
                    "directive": self.node.message,
                    "subdirectives": subdirectives
                }
            )
            
            return spawn_operations