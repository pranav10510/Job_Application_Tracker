"""
Base Agent Class
Foundation for all autonomous agents with LangGraph integration
"""

from typing import TypedDict, Annotated, Optional, Dict, List, Any, Callable
from langgraph.graph import StateGraph, END
from langchain_ollama import ChatOllama
from langchain.prompts import ChatPromptTemplate
from langchain.schema import HumanMessage, AIMessage, SystemMessage
import logging
from datetime import datetime
import json
from config import EMAIL_AGENT_MODEL

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AgentState(TypedDict):
    """Base state for all agents"""
    messages: Annotated[List[Dict[str, Any]], "The conversation history"]
    current_task: str
    plan: List[str]
    observations: List[Dict[str, Any]]
    tools_used: List[str]
    status: str  # planning, executing, awaiting_approval, completed, failed
    result: Optional[Dict[str, Any]]
    error: Optional[str]
    requires_approval: bool
    approved: bool
    iterations: int
    max_iterations: int


class BaseAgent:
    """Base class for all autonomous agents"""

    def __init__(self, model_name: str = None, temperature: float = 0.7):
        # Use config default if not specified
        if model_name is None:
            model_name = EMAIL_AGENT_MODEL
        self.llm = ChatOllama(model=model_name, temperature=temperature)
        self.tools = {}
        self.graph = None
        self.max_iterations = 10
        logger.info(f"Initialized {self.__class__.__name__}")

    def register_tool(self, name: str, func: Callable, description: str):
        """Register a tool that the agent can use"""
        self.tools[name] = {
            'function': func,
            'description': description
        }
        logger.info(f"Registered tool: {name}")
    
    def create_initial_state(self, task: str, **kwargs) -> AgentState:
        """Create initial state for agent execution"""
        return AgentState(
            messages=[],
            current_task=task,
            plan=[],
            observations=[],
            tools_used=[],
            status="planning",
            result=None,
            error=None,
            requires_approval=kwargs.get('requires_approval', True),
            approved=False,
            iterations=0,
            max_iterations=self.max_iterations
        )
    
    def think_node(self, state: AgentState) -> AgentState:
        """Analyze situation and create plan"""
        logger.info("Agent thinking...")
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an intelligent planning agent. 
            Analyze the task and create a step-by-step plan.
            Available tools: {tools}
            
            Return your plan as a JSON array of steps:
            ["step 1", "step 2", "step 3"]
            """),
            ("human", "Task: {task}")
        ])
        
        tools_desc = "\n".join([f"- {name}: {tool['description']}" 
                               for name, tool in self.tools.items()])
        
        chain = prompt | self.llm
        response = chain.invoke({
            "tools": tools_desc,
            "task": state['current_task']
        })
        
        try:
            plan = json.loads(response.content)
            state['plan'] = plan
            state['status'] = "executing"
            logger.info(f"Created plan with {len(plan)} steps")
        except json.JSONDecodeError:
            # Fallback: parse as list
            lines = [line.strip() for line in response.content.split('\n') 
                    if line.strip() and not line.startswith('#')]
            state['plan'] = lines[:5]  # Limit to 5 steps
            state['status'] = "executing"
        
        state['messages'].append({
            'role': 'assistant',
            'content': f"Plan created: {state['plan']}",
            'timestamp': datetime.now().isoformat()
        })
        
        return state
    
    def act_node(self, state: AgentState) -> AgentState:
        """Execute next step in plan using available tools"""
        logger.info("Agent acting...")
        
        if not state['plan']:
            state['status'] = "awaiting_approval"
            return state
        
        current_step = state['plan'][0]
        state['plan'] = state['plan'][1:]  # Remove completed step
        
        # Determine which tool to use
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an action execution agent.
            Given a step, determine which tool to use and what parameters.
            Available tools: {tools}
            
            Return JSON:
            {{"tool": "tool_name", "params": {{"param1": "value1"}}}}
            """),
            ("human", "Step: {step}\nPrevious observations: {observations}")
        ])
        
        tools_desc = "\n".join([f"- {name}: {tool['description']}" 
                               for name, tool in self.tools.items()])
        
        chain = prompt | self.llm
        response = chain.invoke({
            "tools": tools_desc,
            "step": current_step,
            "observations": state['observations'][-3:]  # Last 3 observations
        })
        
        try:
            action = json.loads(response.content)
            tool_name = action.get('tool')
            params = action.get('params', {})
            
            if tool_name in self.tools:
                result = self.tools[tool_name]['function'](**params)
                state['tools_used'].append(tool_name)
                state['observations'].append({
                    'step': current_step,
                    'tool': tool_name,
                    'result': result,
                    'timestamp': datetime.now().isoformat()
                })
                logger.info(f"Executed tool: {tool_name}")
            else:
                state['observations'].append({
                    'step': current_step,
                    'error': f"Tool {tool_name} not found",
                    'timestamp': datetime.now().isoformat()
                })
        except (json.JSONDecodeError, Exception) as e:
            state['observations'].append({
                'step': current_step,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            })
        
        state['iterations'] += 1
        
        return state
    
    def reflect_node(self, state: AgentState) -> AgentState:
        """Evaluate results and decide next action"""
        logger.info("Agent reflecting...")

        # Quick check: if plan is empty, go to approval immediately
        if not state['plan'] or len(state['plan']) == 0:
            logger.info("Plan completed, moving to approval")
            state['status'] = "awaiting_approval"
            state['messages'].append({
                'role': 'assistant',
                'content': "All planned steps completed. Ready for approval.",
                'timestamp': datetime.now().isoformat()
            })
            return state

        # Quick check: if we have enough observations, finish
        if len(state['observations']) >= 3:
            logger.info("Sufficient observations gathered, moving to approval")
            state['status'] = "awaiting_approval"
            state['messages'].append({
                'role': 'assistant',
                'content': f"Gathered {len(state['observations'])} observations. Ready for approval.",
                'timestamp': datetime.now().isoformat()
            })
            return state

        # Otherwise continue with remaining plan
        state['status'] = "executing"
        logger.info(f"Continuing execution. {len(state['plan'])} steps remaining.")

        return state
    
    def approval_node(self, state: AgentState) -> AgentState:
        """Present results and wait for approval"""
        logger.info("Awaiting user approval...")
        
        # Compile results
        result = {
            'task': state['current_task'],
            'observations': state['observations'],
            'tools_used': state['tools_used'],
            'requires_approval': state['requires_approval'],
            'timestamp': datetime.now().isoformat()
        }
        
        state['result'] = result
        state['status'] = "awaiting_approval"
        
        return state
    
    def should_continue(self, state: AgentState) -> str:
        """Determine next node in workflow"""
        if state['iterations'] >= state['max_iterations']:
            logger.warning("Max iterations reached")
            return "approval"
        
        if state['status'] == "planning":
            return "think"
        elif state['status'] == "executing":
            return "act"
        elif state['status'] == "awaiting_approval":
            return "approval"
        else:
            return END
    
    def build_graph(self) -> StateGraph:
        """Build LangGraph state machine"""
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("think", self.think_node)
        workflow.add_node("act", self.act_node)
        workflow.add_node("reflect", self.reflect_node)
        workflow.add_node("approval", self.approval_node)
        
        # Add edges
        workflow.set_entry_point("think")
        workflow.add_edge("think", "act")
        workflow.add_edge("act", "reflect")
        
        # Conditional routing
        workflow.add_conditional_edges(
            "reflect",
            self.should_continue,
            {
                "think": "think",
                "act": "act",
                "approval": "approval",
                END: END
            }
        )
        
        workflow.add_edge("approval", END)
        
        self.graph = workflow.compile()
        logger.info("Agent graph compiled")
        
        return self.graph
    
    def run(self, task: str, **kwargs) -> Dict[str, Any]:
        """Execute agent workflow"""
        logger.info(f"Starting agent run: {task}")
        
        if not self.graph:
            self.build_graph()
        
        initial_state = self.create_initial_state(task, **kwargs)
        
        try:
            final_state = self.graph.invoke(initial_state)
            logger.info("Agent run completed")
            return final_state
        except Exception as e:
            logger.error(f"Agent run failed: {e}")
            return {
                'status': 'failed',
                'error': str(e),
                'task': task
            }
    
    def approve_and_execute(self, state: AgentState) -> Dict[str, Any]:
        """Execute approved actions"""
        logger.info("Executing approved actions...")
        
        if not state.get('approved'):
            return {'error': 'Actions not approved'}
        
        # Override in subclasses for specific execution logic
        return {'status': 'executed', 'result': state['result']}