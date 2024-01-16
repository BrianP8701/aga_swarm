this file is not meant to be read but i like keeping it up 

We want functions that can:
    Take text describing a function
    Return a function

In addition we need the option to:
    Generate test cases for the function
    Make the function executable
    Run the function with the test cases
    Save the function
save the function, test the function

We want an agent that can:
    Take a function and a set of arguments
    Return the result of the function

## Agents


## Functions Config
json file with:
    function name
    function description
    function arguments
    function return type
    function test cases
    function code
    function dependencies

### Who can call functions?
there is one global entrypoint to functions: exec_function()
It checks if the 

### Initial Functions:
- create_assistant()
- create_function() 
- create_test_cases()
- test_function()
- save_function()



All of the above initialization will happen in what is called a 'toolkit'



okay fuck scrap the toolkit.

## Swarm flow in my head 1
Create head agent
Pass goal to head agent through chat()
Take output of chat(). Spawn a new standard agent with the output of chat() as the instructions

In order to write functions that interact with other functions, an agent needs to:
    1. be aware of the other functions
    2. be able to call the other functions

To be aware of other functions we need to include in the context all the function names, descriptions and parameters

There are some flows that are concrete, like the one aforementioned. But how can the swarm autonomously create and access new flows?

# Tool creation... were finally actually at the point where i can do it
okay.. okay...
so i now have the route subtasks down. the current flow is 

1. pass goal to swarm
2. swarm breaks goal down to smaller goals
3. swarm routes each goal to next task 

Now the "next task" could be anything like retrieve information from the web, github, some other api. Write or perform some action. Either way, the point is we might not have the capability to perform this next task. So we might have to 



One key thing is we dont want to break down tasks too much. Id rather opt for a swarm that tries to accomplish a task too early and realizes it has to break down more than one that frequently breaks down tasks too small.



having an agent write test cases for a piece of generated python code is challenging cuz depending on the code we might need an object that involves other shit... and the output is not a clear cut type, its dynamic... so first we need an agent to produce a tool schema for that code.




_________________________________________________________________

Ive made the agent that breaks down goals and the one that routes goals.... but now im confused. Im trying to write the "write_python" function:


from swarm.swarm import Swarm
from swarm.agent import Agent
import json
async def write_python(goal):
    swarm = Swarm()
    task_handler = swarm.task_handler
    python_agent: Agent = swarm.agents['write_python_agent']
    python_test_cases_agent: Agent = swarm.agents['python_test_cases_agent']
    
    tool_output = await python_agent.chat(goal)
    python_code = tool_output['arguments']['python_code']
    
    test_cases = 
    
    # Create test cases for function
    with open('tool_building/config/test_cases.json', 'r') as file:
        test_cases = json.load(file)


okay. calm down. recollect.
The assumption im making is that if the problem has been broken down enough, and we gather all the relevant context and information to solve the problem chatgpt should be able to solve it.

"Solving it." Ultimately, tasks get broken down into one of the following: [Write code, retrieval, run code] (for now)

First lets focus on the task of "writing code"

When writing code we need to gather all relevant context. Here's some examples:
    - If the code works with some class we previously made, we need that class in context to see how it works
    - If the code is a piece of a bigger project or process we need a comprehensive description of the architecture the code being written now will be put into
    - If the code is using some library we'll need to have the relvant documentation or actual code from that library in context potentially.

In doing this little exercise above... I realize one thing. Part of me previously believed what would happen is we break down the task into smaller pieces, and then at the bottom that agent will do a retrieval of whats relevant. But now part of me sees that in breaking down the task we might need context along the way to break down the task correctly.


so now i talked to myself a bit more. i kinda ranted abt my concerns.... whats the solution? Remember we want simple.... it needs to be simple.

theres rlly quite a lot of things the swarm needs to be capable of doing before becoming self sufficient. And it can become sel sufficient but be extremely sub optimal. I reckon... we gotta hack shit and optimize as we go. ahh back to the same old adage.

so we start simple. just write the python and save it. we'll assume the code will get written correctly. for now, dont worry about making test cases, debugging or complex retrieval. we'll start with a simple goal that wont need that then scale up.

_________________________________________________________________________________________________________

so first we try to have the swarm build a github class. 
then have it save and make it available to itself.

Add web scraping tools, pdf scrapers
save data locally and to database. Have a global VIEW of all data, and function describing how to get it if its local or on cloud
Add all of the above as functions

have the swarm create new functions to write code in different languages.
try to find ways to make the system more robust when it makes wrong decisions or errors in code
create a better user interface to allow the user to provide input while the swarm is running
Then try to have the swarm construct a web app (real estate autogen CMA's, chat, leads, zapier routing etc)
Try to have the swarm go over its own code and generate documentation describing itself, upgrade itself, add typing hints etc

As our database for the swarm grows we're going to need to create multiple different rag implementaions. one with embeddings-chunking strat, one with knowledge graph/folders, and more etc.


_________________________________________________________________________________________________________

# Tree structure
There are 3 concerns i have now:

1. Should i do the tree spawn-terminate method? Is that all encompassing? Is it too rigid and introducess too much complexity?
2. There needs to be places for user input. I have a temporary answer to this. Now initially, i can make it so that we have user input and verification at every step. I know, the point is that i want to automate the process, but initially this will make it easier, and it will also be easy to take this away later
3. This current task is very easy for a human. Im spending more effort getting the swarm to do it than itd take me alone. but - the key is that im automating this whole level of difficulty and type of task

The question is first and foremost how do we implement tree architecture?

Tasks are nodes. Tasks can spawn other tasks. 

TaskNode - we'll call them tasknodes. 

TaskNodes:
    - type (str)
    - children (List[TaskNode])
    - parent (TaskNode)

    - spawn new TaskNodes
    - terminate themselves and report to parent


Now, before we introduce these changes, lets review the current abstractions in place for tasks

We have a task type which holds the function name to be called in functions config and the corresponding parameters to be passed. Its a one time use thing.
Then we have the TaskHandler object which takes a task and runs it. very simple rn.

What i see now is that the forward pass and backwards pass through that Node will likely require us to call different functions. On the way down, we'll need to perform and decide what to do next. On the way up we'll be reviewing reports and seeing if our task is done and if we can terminate, or if we need to try again.

So the question is, at each Node is it as simple as having two functions, one for forward and one for backwards pass? Remember the age old adage - we want it to be as simple as possible to avoid complexity, but the swarm needs to be universally applicable and infinitely scalable.


________________



# Tree Implementation for Swarm

Fundamental unit is the node which consists of:
- TaskType
- Unique data
- Parent
- Children

What this means for simplicities sake is that each node cannot do internal review, rather it must spawn a new node to do so

Additionally the swarm must now maintain two more things:
- The curresnt state of the tree
- The history of the tree

Schema for swarm history (JSON):

create node
run node
delete node

[
    {
        action: "create_node",
        node: Node
    },
    {
        action: "run_node",
        node: Node
    },
    {
        action: "delete_node",
        node: Node
    },
    ...
]


When the swarm ends its run we must save a snapshot of the current state of the swamrm that is recreatable

Schema for swarm snapshot (JSON):
{
    population: x,
    nodes: {0: root_node, 1: node1, 2: node2...},
    task_queue: [(task, queue), (task, queue)...]
}

Now one challenge with taking the snapshot is at the time of deletion the task being performed at that moment will not be included in the snapshot


So now, when we implement this we'll be able to pick up where we left off with snapshot and get a good visualization with history


each node must now:
perform their task
save their output within themselves
save state and history
create children or terminate

OKAY I GOT IT. The functions in functions.py should not contain the logic related to nodes at all. 
Where does the loop go? What does the loop handle? Execution of tasks? Creation, deletion and activation of nodes?
Now the thing is functionally it doesent matter. Why does this decision matter? Because it affects the way we think about the swarm. 
If we think about the swarm as a loop that executes tasks, then we have to think about the swarm as a loop that executes tasks.
If we think about the swarm as a loop that creates, deletes and activates nodes, then we have to think about the swarm as a loop that creates, deletes and activates nodes.
The second way of thinking about it is more general. The first way of thinking about it is more specific.
The loop defines the level of granularity that will be easy for us to visualize and 
Oh shit i got it. At what granularity do we want to save state? Thats what matters for the swarm. 

To save state we need:
All the nodes

The reason we have history and state is because the current state of the swarm doesent show us how we got there as the swarm will delete nodes. So for history, to see how we got to the current state we need more.
We need all instances of node creation, execution and deletion

So that answers our question. We will have a queue in the swarm responsible for three tasks creation, execution and termination of nodes. this queue shall be called: node_lifecycle_queue
# Swarm coding Challenge

Okay I've identified a big challenge in the RAG portion of this project. When i have the swarm write code its going to need to write code to interact with the rest of the swarm and *squeeze* itself in. Okay lol i just thought of the solution.

Create an internal swarm api. And make good documentation on usage and functionality and just pass that to thw swarm whenever it is necessary. 

Now, when the swarm then needs to interact with other libraries or apis, its going to need to retrieve that documentation or code. in fact, we need to somehow do retrieval over the docs to find the relevant portion of the docs/code to add to context. Effective autonomous RAG is crucial for self sufficient swarm capabilities.











# Refactor structure plan for the future #TODO
So now i kinda have better thoughts.... ima need a big refactor but ima push features for a little longer because the complexity rn is still managable for my brain. But when I do refactor heres a rough structure:

- Swarm (Tree structure, nodes, state, history)
- TaskMaster is responsible for execution of all functions (task_queue)
- Internal Swarm API (minimal functionality for self sufficiency. This is some theoretical bound)
- Memory (Storing data, documentation and also code, classes etc to be used by the swarm)
- Human Interface (Terminal for now, but later a web app including visualization with easy access to communicate and interact with the swarm as it works)

Okay. so this actually helped clear up my head a lot. We get the swarm and taskmaster done once and for all, and then there should be no further iteration added there.

The internal swarm api will take time and lots of iteration to get right. But once its right, the swarm will be able to do anything.

The memory will be iterated on for all eternity. 

The key thing is that the internal swarm api needs to contain the rag functionally to effectively navigate the memory. thats what it all comes down to.














# Theoretical non rigorous thinking abt the internal swarm api

Okay... so what do we need to include in the internal swarm api for self sufficiency? specific fucntions:

- break down goal
- route goal
- write code/text
- save code/text so it can be used
- execute code
- retrieve context from memory




_____________________________________________________________________________________________

create node -> execute node -> create node, create node, create node -> execute node, execute node, execute node -> ... -> terminate node, terminate node, terminate node

okay the crucial thing is when a node terminates, it terminates itself and signals its parent to execute. a parent cant execute unless all of its children have given it the go. then it terminates itself and the process continues.

When we spawn a node, we spawn it and execute the node. That node is responsible for internally deciding whether to terminate or spawn children. 

so if we have the lifecycle queue in the swarm be responsible for two things:

- spawning nodes
- terminating nodes




## Creating/spawning nodes

This is my thought process writing the _create_node() function in swarm:

Well the node is actually already created. it has the task type, data and a pointer to its parent.
Now you need to save to history the fact that this node was created.
Save to state the node prior to execution
Then execute the task
Then save to state the node after execution
And save to history the fact that the node was executed

Now the question is, do we create/terminate nodes inside the task run, or seperate but inside the node?

Will every node use an LLM? Or will some just execute code?
Okay, not all nodes will use an LLM. Some will just execute code.

So lets clear up.... we need the node to be very general. lets think of all the things we want a node to be able to do:

- break down goals
- route goals to appropriate next tasks
- write text
- write code
- execute code
- read terminal output
- go back up and retrieve outputs from previous nodes
- browse the web
- interact with internal swarm api
... and many more

now that im looking at this... i take back what i said earlier. it does seem every node task is coupled with an llm interaction. cuz we can combine write & execute code, and etc.... Hmmmm.... lets see can i think of a node that would not involve the use of an llm...

okay so i talked to chatgpt... he complimented me and i let it feed my ego for how "complex" my project is. but anyway i came to the conclusion that i want each node to call an llm with this reasoning:

"I mean i think for my feel the swarm will take predefined routes and paths of logic, and the llm reasoning engine helps you know... automate my knowledge work and that should be what defines the granularity of a node. every node is one llm call."

So now we decided every node has:
type, data, parent, children, output

Each node will execute its predefined logic, and do an LLM call to automate a piece of knowledge work, and will then either execute some more logic then create a new node or just create a new node. So this means every node is associated with an agent + predefined logic. Now, how should we implement the flow of the node?

So the node has its type attribute which should link us to the logic and agent used in this node. It could be:

-> agent ->
-> logic -> agent ->
-> agent -> logic
-> logic -> agent -> logic

Okay each node is associated with a script. The script is stored as a string in one of the configuration files. executing the node is just executing the script. output is simply the output of that script. Included in the output is all the data needed to spawn the next set of nodes or to terminate self. We want to decouple swarm interaction from the script for simplicity purposes

all scripts will be run from the same place so import statements wont fuck up. all scripts are seperate and meant to run on their own

now the question is, actually 3 questions:
- are all scripts in python?
- where should i store the scripts?
- what metadata should i store alongside each script?

well lets just put language as metadata
store the scripts as strings in json file in config folder... but potentially in new folder later. thing is we'll probably have thousands and just more and more scripts in the future. this is where rag file system/tree comes in to organize navigation 


node_scripts.json:

{
    node_type: {
        language: str,
        description: str,
        script: str
    },
    ...
}

can add more metadata later as needed
most importantly, later on we're going to have to find better ways to organize and navigate the scripts and tools available to the swarm as it grows bigger



# Router

A question im saving for later, is rn the router has the choices:
['break_down_goal', 'write_text', 'write_python', 'retrieve_info', 'ask_user_for_help']

But how do we 'route' when we have many hundreds of options to route to?




Remember when we terminate a node we dont just go up to the most recent fork in the tree. some managers didnt do inparralel at break but had a plan with steps so u need to pass back to them



# Incorrect abstraction

Some abstraction is wrong. specifically, a naming issue. It doesent seem intuitive.

Primarily, the part where we "spawn" a node in the main loop, when it is already spawned and we really are just executing it.

So here is the actual flow of what is going on:

1. We have a node blueprint without output data
2. We then instantiate the node object and add it to the lifecycle queue
3. The lifecycle queue will receive the node and execute it.
4. Based off the output of the node we will either:
    - receive node blueprints for children and go back to step 1
    - begin termination process for node

Here are the current naming conventions i have for each step:
1. 
2. create_node()
3. spawn, terminate
4. 
    - create children
    - terminate

i think better naming is just one small change:
1. 
2. spawn_node()
3. execute, terminate
4. 
    - spawn
    - terminate



# Testing offline

So i am currently on a plane and have no internet so im gonna add testing without api calls to test the terminate spawning flows of the tree.

So to do offline testing i essentially need to mimic and make up the openai output as thats the only use of network, everything else is offline local

So lets just make up our own fake scenario:

goal: determine the root cause of aging
routed to : break_down_goal
parralel -> retrieve_info, write text

We will need to retrieve: Most recent and well peer reviewed research on causes and solutions to aging and what are the primary unanswered questions/ bottlenecks

We will need to write text detailing a plan to do x


goal > router
goal > manager > retrieval, write_text
retrieval
write_text

so an offline_test method in swarm





# THinking about when we have more tools

Okay fukc it lets just listy off all the potential tools we might add:

router
manager
write_python, write_java, write_javascript, write_english...
browse_web
save_code
run_code (return output of code in terminal, error or any print statement)
retrieval (Links u to the option of browse_web, search through swarm database)


Fundamentally this becomes a retrieval and memory management problem





# Swarm

Fundamentally what is the purpose of the swarm? Specifically, i mean the way im building this out, this architecture with a tree? Why do i have asynchronous stuff? What im doing could easily be done synchronously, sequentially.

Im doing this for efficiency and dare i say scalability? Efficiency obviously because we'll have llm calls running in parralel, more and more the deeper we go down the tree. And scalability.... well tbh we already discussed this part. so far our 'swarm' system we are building locally is very fast and efficient with the only bottleneck being the llm calls.

bruh, okay but this could be horizontally distributed need be. idk i just wanted to think about how this might grow with scale now but i guess thats a problem for another time. I just finished reading alex xu's system design interview book a couple days ago in iceland.




# Github api class

goal: create a class that has all the functionality to interact with github repositories
mapped to write_python
got the code, the class string
save the code
generate test cases for the code and run it
take the output




# logging

Well the thing ise we definitely want to integrate python logging into the swarm, not only for the purposes of debugging the swarm, but also for the purposes of debugging the code that the swarm writes.

The question, as always is how do i implement this? One of the clear problems that arise now is that im noticing that im spending lots of time overthinking how to implement this stuff, what is the best way, trying to predict into the future... i should just move faster and aim for action and code writing.

Okay so how i ought to implement logging?

We already have the functionality written to save state and history in json format. this allows us to resume running the swarm from where it left off previously and to retrace the swarms every step. thats good. tbh the only place to add python logging in the swarm is for debugging when it fucks up

The second place i need logging is to test the code that the swarm writes. I need to be able to see the output of the code and the output of the test cases. Now these definitely do ought to be seperate. 

Now here is the question. i dont want the code written by the swarm to contain logging... but i might have no other choice. What i might have to do is have the swarm write the code 

# Potential conflicts with the swarm writing code 

- Testing
    Testing can vary very widely. It might be a singular unit. Or it might be more tightly coupled with the rest of the system. It might require further user input, like a key or url. How do we actually test it, see the errors or if it did well? We might need to use logging, we might need to save output to somewhere else and check if it did whatr it was supposed to afterwards. We might have to generate test cases. Essentially, we'll have to after writing the code pass the code to a tester who will consider all these possibilities and act accordingly.
- Naming conflicts. As the scale of the swarm grows we might reach a point where we have naming conflicts.
- Saving the code. As scale grows and we have lots of code we will need to organize everything in a file system/tree that the swarm can navigate to find the code it needs to work.   



____________________________________________________________________________________________________________________________

# On where to add user input, retrieval etc

we can add an option to every agent to opt out of performing its task and to ask for user input or more context, and to not just check a box asking for it but to output a string asking its actual question. This way we can have a more dynamic system where the swarm can ask for more context or user input when it needs it.

OOOHHH another cool detail while writing a much more in depth prompt for the agents and adding a place for user input, i can have the agents in the swarm identify inefficienciues or improvements in the swarm if i give each of them enough detail abt the swarm and what role they play/where they are. for example at the bottom of the managers prompt i say: "Your insights and further questions are welcome as we refine and optimize this swarm system. Let’s discuss any aspect of the plan where you think improvements or clarifications are needed."


Okay im adjusting my agent prompts and changing them to give them options to retrieve context or ask for user input and im reaching a few questions. So ive already concluded that each agent should be able to ask the user or retrieval agent questions. Im confused about:

- Do i give the manager agent an is_parrallel choice or just have it output a list of immediate goals?
    This depends. In the code do we come back to this agent to review and make the next decision or does it get terminated and another agent does review and next decision? Where does review happen is the question? Do we have a seperate review agent or have review happen within the agent? review within the agent fosho. review within the agent fosho. SOoooo like... hmm. Itll be aware of what it wanted accomplished. And then its children will pass it a report. and then it will decide to terminate or create new children. so no in parralel. just output immediate goals to be done now.



Okay this is 2 days later still working on where to have the agents stop and ask questions. What type of questions might arise?
- Question might need to be directed to user
- Question might require searching the web
- Question might requiring searching through the swarm internally

So questions can get mapped to many different places. For now let's not concern ourselves with that. Just where do we have the agents ask questions and how? 

For some reason im having a really big problem now. My first instance of the model failing to output my defined json schema. The python coder is outputting all parameters expect the python_code, despite the fact that its in the required section. I wanted to have one api call giving it the option to either: ask question output no code OR output code and ask no questions. But the model failed to ask questions or output code. So i thought, okay maybe this is to much for the model to handle.... maybe i need to break it up so now i have an agent to ask questions and one to write code, but now no code is getting written!!!! wtf!!

router - no questions, just ask user to choose it if cant decide
manager - ask questions
code analyst - ask questions

# JSON Mode Issues
well this is good news and bad news. What we see is that json mode is not reliable. i tried looking online but cant find anything in particular to help increase reliability. Obv there are methods like finetuning and giving examples but that for later down the line. (btw fine tuning is not abt fine tuning. SOTA model will always change its abt having data for my system. then i can just refinetune whatever SOTA model is on that) So what are some things i can do to increase reliability? THere is no science to this, just intuition but here i go:
- Less complex requirements
- Smaller tasks
- Use enums
- set required json mode 

The thing is i wanted to pass my data in one time 
Data -> questions or answer
but this might be too much for the model to handle. it might be better to:
data -> questions -> data -> ... until no more questions
data -> answer
This is more costly.... but might be more reliable? Should be more reliable. dumbass ai cant do shit(im joking i was just mad spent hours yesterday fucking with this problem)

okay. well now why is this good? Cuz everyone else is dealing with this problem... and while this problem exists theres no way u can have huge autonomous ai systems... which is the reason we dont see them today. 

Bro lmao this thing man. it.... nvrm.. this llm just did some shit that was dumb but smart at the same time. like its breaking the rules but in a good way 


# what next... ??
okay... um so ive kind of passed the first border. weird i dont feel any bit of satisfaction. well now its time to upgrade to a harder goal. lets choose a goal that will require ideally:

More user back and forth
Actually multiple pieces of code the system will write that will have to interact together
web scraping maybe?

oooh boyyy!!!!! This means were gonna start implementing some RAG methods!!! ABt goddamn time.

oh shit wait. i forgot. i need to implement the terminate functionality first. oh yeah lets do that and THEN were done with the simple goal. The swarm needs to self terminate once the goal is accomplished. 

sooo terminaton huh. So we have this simple goal of create a tictactoe game.

router -> python_coder
very simple. We can force it to go through the manager by just telling it so we can make sure all the pieces are working:
router -> manager -> router -> python_coder

we might as well add some testing here. this is a really easy place to start. in the future we could have a seperate contrainer to do testing. but here we could just have the python tester run the tic tac toe script.

so after the python coder finishes writing the code, we can pass the code name to the python tester... who will have to decide how to test it. it can output a plan to test the code

python tester planner


BRUHHHH FUCKING FUCKS SAKE. so the python coder didnt output fucking tic tac toe code the second the time, im almost sure it did the first time. Okay i think i have a solution to this. split it into another two steps, one where its SOLE TASK is to just output the python code, and then a second time where it is to generate the other parameters. the metadata for the code. so we have a new agent synthetic_python_metadata_extractor


# Autonomous script testing
so ima be honest with myself - i might be pushing the limits of the model with trying to implement autonomous testing. But i still want to have it in there and just have a catch where i can step in if it fails rather just giving up and just dooming it to user input. so here is the flow with script testing: (im starting with testing standalone scripts cuz thats easiest)

- we start with a script and its description generated by the python coder
- we pass it to the Python Script Test Planner Agent to determine a few things:
    - is the script executable as is?
    - can the llm generate synthetic input data?
    - does the user need to provide input parameters?
- If the script isn't executable as is gather input params from user if the planner says so and pass all this info with the code to the Python Script Test Generator Agent who will return an executable script. this is what im assuming will be a major failpoint. The agent will also have to add logic to save the relevant outputs to the right place in a given json path if the script succeeds
- Then download dependencies from the dependency list provided by the python coder
- Run the script and if there are errors save them to the same place where we would have saved success messages
- If at any point in this process we fail, we save the script to a .py file in the testing grounds, and let the user go in their himself and prepare the script, and the user will signal to the system when he is done by saying something in the terminal, and the system will pick up from there. 



# Namespaces




# Reorganizing repo
okay so im reorganizing the structure of the repo massively. let me share where im at now, and lets plan:

.
├── LICENSE
├── README.md
├── journal.md
├── past_runs
├── reference
│   ├── autogen_reference.py
│   ├── openai_config.py
│   ├── openaiapi_reference.py
│   ├── settings.py
│   └── utils.py
├── scripts
│   ├── helper_script.py
│   └── manual_write.py
├── swarm
│   ├── config
│   │   ├── agents.json
│   │   ├── agents.md
│   │   ├── config_docs.md
│   │   ├── node_scripts.json
│   │   ├── node_scripts.py
│   │   └── synthetic_code.json
│   ├── core
│   │   ├── agent.py
│   │   ├── memory
│   │   │   ├── manual
│   │   │   │   └── hello_world.py
│   │   │   ├── testing_ground
│   │   │   │   └── python_scripts
│   │   │   │       ├── schema.py
│   │   │   │       └── test_results.json
│   │   ├── node.py
│   │   ├── swarm.py
│   │   ├── task_handler.py
│   │   └── utils.py
│   ├── openai_config.py
│   └── settings.py
├── testing
│   ├── temp_unit_testing.py
│   └── test.py
└── todo.md

i removed some of the pycache files and the runs inside the past_runs folder. So let me explain the current state

past_runs folder contains history and snapshots of the swarm while im testing. a temporary folder for now. one day this will all be on cloud and a web app/gui
reference contains reference code, just pieces of code i might use. this is gitignored
scripts contain standalone scripts for the swarm. important and will forever be a thing
swarm is the main folder
    config contains stuff the swarm needs like agents and functions for nodes. its also a place for the swarm to save code its written
    core contains core classes for agents, nodes, handling tasks and utils for the swarm.
        the memory folder contains a place for the swarm to test its written code
testing is for testing obv.

okay so what things do i want to change now? 
1. I want to break up the config folder
2. I want to fix the mess that is the memory folder... nothing feels right there.

well. one of the big realizations ive made... 

bruh okay im back i just broke the whole config folder up. its way better now whew. now theres a folder dedicated for agents, where each agent has its own folder with a folder for their tool, prompt and script.

now next... the synthetic code generated by the swarm, and its testing. where do these get saved? Lets list out all the stuff we have

- generated synthetic code
if the swarm is creating a project itll be saved and tested in some seperate folder and ran in a seperate enviroment. if the swarm is creating some wrapper class or script it thinks it will itself use it can be saved somewhere within its memory. this code that ***might*** be used should be seperated from the core functionality that is necessary for the swarm to be self sufficient, which is called the "internal swarm api".
so what about things like the swarms terminate spawn methods, task handlers? those are internal swarm api things. the actual CORE of the system. 
the rest of the code will need to go in memory and be dynamically managed. so should the memory folder go in the swarm folder or at the root? the root cuz itll get BIG.
also quick note... this is so obvious but theres no need to always have to store code as strings. 



# Reading 2023 RAG survey paper
Interesting quote: "Additionally, it is suggested that LLMs may have a preference for focusing on readable rather than information-rich documents."
One thing to note, is that in my swarm most of my rag will be over structured data, data structured as dicts. but just for a layer, under that we get to unstructured text and code etc

searching over documentation requires common rag, like embedding nearest k.
searching in a codebase requires structured rag

potential tools for rag agents:
recursive retrieval
iterative retrieval
small to big chunking
reranking k results
rewriting query
compressing and verifying retrieved hits
multiple indexes for same document
indexing raw text, metadata, summaries, extracted info, different combos etc


# Debugging swarm with new organization

Essentially we should have a detailed description of the tree/file structure of our project to allow the swarm to autonomously navigate it to find what it wants. in addition to allow it to reorganize the file structure and write code to interact with different pieces on its own.

like i have a couple pieces now i already talked abt above yesterday: testing, synthetic code, manual place for user to prepare scripts for testing, documentation for the swarm. so i suppose how will context retrieval really work? some agent will have task X and will require context which may be code, documentation, results of some other agent or test etc. the retrieval agent will be like a router agent but to navigate over memory:

- structured code search
- rag query
- web search

so yeah. i guess we have the one memory folder to hold it all. and a memory router or retrieval router to navigate it

retrieval router, action router. when the quantity of options grow to large we need to break it down into sections and layers, a tree with clone nodes allowed. the routers navigate the action and memory tree. the swarm can create new actions and memories of its own. oh yeah baby now we're onto something.

all the actions are agents
any history, state, synthetic code, docs is memory

okay i guess here is whats bothering me. i want one place for memory, which ive done now. lets say i want to save something like a new python script that was generated

i want to make examples of the memory and action trees. just so u can see what i mean. These need to be autonomously configured - in the future. not yet. dont overwhelm myself yet. for now i can organize the action and memory space.


                            ------- memory router      ----- script
                            |                          |
                            |   -------- python ------------ class   
                            |   |                      |
            retrieve info ---   |------- java ----     ----- function
            code ---------------|                      
action ---- write
            test
            break down goal
            user interaction


actually the initial layer can be more abstract


             write
action ----- code
             test

whatever im not doing this its taking too long to type out.
okay so i get the action space is a tree. and the memory space is a tree. now one thing i gotta implement now is namespaces

okay i need to make a dynamic router... meaning a router agent where i can pass a list of options along with an optional further description of each option to the router.
the only problem is my whole architecture as of now has it so that the tools and prompts for agents are static. i need to make them dynamic.

ah god do i need to make a unique object for the router agent? i wanted all agents to follow the same pattern but it cant.... approaches i can take:

- have router, manager, optimizer, coder, writer agent in internal swarm and rest be in external memory? well ultimately.... fuck like writing code is something that can be done 

Memory Router (list of options)
Action Router (list of options)

Manager (goal/action statement)

Coder(goal/action statement)

Writer(goal/action statement)

not every llm call has to be called an agent right? fuckk my abstractions were wrong. bro im lost now. fuck fuck fuck. cuz the router needs dynamic input. ahhhhhhhhh

what do i do bro fuck there does need to be a standard pattern for each agent or no? I guess.... no? each agent just needs clear documentation describing how to interact with it. each agent needs an api for itself. 


should there be a single router for memory and actions or one for each? Whats the difference between both? 


okay so ive created a schema for the action space. the action router recursively navigates the space to find the appropriate action. 

now we need a way to pass this action back to the swarms action loop. 

currently the way this works is the action loop takes a node blueprint which it will create and execute. so each action in the action space corresponds to a node which corresponds to a script is that correct? i guess it is...

the node blueprint contains a path to the corresponding action in the action space.

This action... could be an agent we've defined and made ourselves. 

nah okay it cant just be an agent. it has to be more dynamic then that. what i reckon is the action space is replicated as an actual file system in the actions folder and each leaf node is a folder which is like its own little package. now we cant confine the action to be a class and u must run the main method. no, it should be... 

each action should be in its own scope, its own namespace, its own package, seperate. Each action should have a docs.md file describing how to run it.... and the executor node is assigned with executing actions.

ideally we dont want to waste unnecessary tokens and llm calls to execute a node... what are the paths?

Well an action is a predefined piece of code to run. the router is always passing merely a goal and nothing more. are there any scenarios where between two different nodes we need to pass more than just a directive? Context obv but that comes from retrieval... when a coder writes code it needs to figure out where to sdave the code. one approach is to always have the same way to exexute an action package, say a file main.py with a main method to execute. but what if i have things with other languages?

wait a second. after implementing the router that recursively searches the action space i realized that it doesent need dynamic input, it just takes a single directive. okay thats good news, maybe i dont have to change the architecture. are there any agents/actions that will require more input than can be in just a string?  irdk.... i rlly cant try to predict these things i just need to implement and move forward and if new functionality is needed, ill deal with that when it arises. 

for now, i can just have a singular way to execute all actions. 

so like would the github wrapper go in memory or actions?

this goes back to the question of how we execute actions. each action should be isolated (it can still import things from memory or other places) It should have dynamic input. 



# Goal 1
Here is the first project im gonna have the swarm work on:

    We want to autonomously prospect potential clients for a real estate agent using the ChatGPT API
    We have csv files with expired listings, peoples names and their phone numbers. Create a full fledged system to prospect these people.
    First, we need to take filters from the real estate agent to narrow down the list of people to prospect.
    Then, we need to send an initial message to each person on the list to their phone number. I'll give you a template for the message.
    Then we need triggers to send follow up messages to people who respond to the initial message.
    We want to continue the conversation and continue to gather relevant information about the person pertaining to their real estate needs.
    We need to save and extract structured data from the convo to a database. I'd like to use GCP.
    We'll also want to be able to alert the agent when a person is ready to call, or when a person is ready to sell their house. If at any point the LLM 
    needs help it should also alert the real estate agent.
    We'll also want to offer things like a free home valuation, a comparative market analysis, and a free home buyers guide.
    We'll expand functionality to include emailing them, and calling them using a model like whisper to cold call.
    We may want to also automate the sending and receiving paperwork.
    You'll need to design the system, build out all the components, save, test and run the code.
    We'll want to have a test area where we can simulate conversations where the potential lead is an LLM.
    We'll want a lot more. But this is a good start. keep working, build out this initial functionality keeping in mind that we'll want to expand it later.
    
    use twilio, gcp. probably google cloud function with triggers and then we'll want some sql database to store the extracted structured data. 

Before we move forward, lets try to think about how we want the swarm to actually go through this so we can answer my many questions... im kinda overwhelmed.

break down goal, make plan ask user questions to clarify. Get the actual file from the user. analyse the schema of the file. Create an area in my local file system to save all the code pertaining to this project. Write data cleaning scripts. write the code to send messages. save all this code to the appropriate place, keep the folder organized. Write cloud functions to continue conversation, save extracted data to database. get cloud keys from user. upload gcfs. test. 

so actions like save code to this path, get file from this path. small functions like that. the swarm is probably gonna be writing lots of scripts to get info, or no. we should definitely have a predefined action node so we can easily compose all these actions. so yes 



# memory agents

Theres a couple memory agents.

Retrieval agent. This agent is like the action router. it navigates the memory tree layer by layer and finds the appropriate memory.

memory router navigates the memory tree to save something to the memory tree. Its very simple and does not create new folders.

optimizer agent. this agent aims to keep the tree balanced and creates new folders when possible

clone agent. this agent replicates data to appropriate folders to make sure they can be easily found, even if a different route is taken.