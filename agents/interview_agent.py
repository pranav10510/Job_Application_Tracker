"""
Interview Preparation Agent
Prepares for interviews using RAG and past application data
"""

from typing import Dict, Any, List, Optional
from .base_agent import BaseAgent, AgentState
from langchain.prompts import ChatPromptTemplate
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class InterviewPrepAgent(BaseAgent):
    """Agent for interview preparation using historical data"""
    
    def __init__(self, model_name: str = "llama3.2:3b", rag_engine=None, db_connection=None):
        super().__init__(model_name=model_name, temperature=0.4)
        self.rag_engine = rag_engine
        self.db = db_connection
        
        # Register preparation tools
        self.register_tool(
            "rag_search",
            self.search_past_applications,
            "Search past applications for similar companies/roles"
        )
        self.register_tool(
            "weakness_analyzer",
            self.analyze_weaknesses,
            "Identify weak areas from past rejections"
        )
        self.register_tool(
            "question_generator",
            self.generate_questions,
            "Generate likely interview questions"
        )
        self.register_tool(
            "study_plan_creator",
            self.create_study_plan,
            "Create personalized study guide"
        )
        self.register_tool(
            "practice_problem_finder",
            self.find_practice_problems,
            "Find relevant practice problems"
        )
        self.register_tool(
            "prep_guide_compiler",
            self.compile_prep_guide,
            "Compile comprehensive preparation guide"
        )
        
        logger.info("InterviewPrepAgent initialized")
    
    def search_past_applications(self, company: str = None, 
                                position: str = None, 
                                industry: str = None) -> List[Dict[str, Any]]:
        """Search past applications using RAG"""
        logger.info(f"Searching past applications: {company}/{position}")
        
        if not self.rag_engine:
            logger.warning("RAG engine not available")
            return []
        
        try:
            # Build search query
            query_parts = []
            if company:
                query_parts.append(f"company: {company}")
            if position:
                query_parts.append(f"position: {position}")
            if industry:
                query_parts.append(f"industry: {industry}")
            
            query = " ".join(query_parts) if query_parts else "all applications"
            
            # Search using RAG
            results = self.rag_engine.search(query, k=5)
            
            logger.info(f"Found {len(results)} similar applications")
            return results
            
        except Exception as e:
            logger.error(f"RAG search failed: {e}")
            return []
    
    def analyze_weaknesses(self, past_applications: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze weaknesses from past rejections"""
        logger.info("Analyzing weaknesses from past applications...")
        
        # Filter rejections
        rejections = [app for app in past_applications 
                     if app.get('status') in ['rejected', 'no_response']]
        
        if not rejections:
            logger.info("No rejections found")
            return {
                'weak_areas': [],
                'common_patterns': [],
                'recommendations': []
            }
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an interview performance analyst.
            Analyze past rejections to identify weak areas and patterns.
            
            Return JSON:
            {{
                "weak_areas": ["technical skills", "communication"],
                "common_patterns": ["Failed at system design round"],
                "recommendations": ["Practice system design", "..."],
                "success_rate": 0.25,
                "areas_to_focus": ["algorithm practice", "behavioral prep"]
            }}
            """),
            ("human", "Past rejections: {rejections}")
        ])
        
        chain = prompt | self.llm
        response = chain.invoke({"rejections": json.dumps(rejections, indent=2)})
        
        try:
            analysis = json.loads(response.content)
            logger.info(f"Identified {len(analysis.get('weak_areas', []))} weak areas")
            return analysis
        except json.JSONDecodeError:
            logger.warning("Failed to parse weakness analysis")
            return {
                'weak_areas': [],
                'common_patterns': [],
                'recommendations': ["Review past applications manually"]
            }
    
    def generate_questions(self, company: str, position: str, 
                          weak_areas: List[str] = None) -> List[Dict[str, str]]:
        """Generate likely interview questions"""
        logger.info(f"Generating questions for {position} at {company}")
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an interview preparation expert.
            Generate likely interview questions for this role.
            Include: technical, behavioral, and situational questions.
            Focus extra attention on weak areas if provided.
            
            Return JSON array:
            [
                {{"type": "technical", "question": "...", "difficulty": "medium", "topic": "algorithms"}},
                {{"type": "behavioral", "question": "...", "difficulty": "easy", "topic": "leadership"}}
            ]
            
            Generate 15-20 questions.
            """),
            ("human", "Company: {company}\nPosition: {position}\nWeak areas: {weak_areas}")
        ])
        
        chain = prompt | self.llm
        response = chain.invoke({
            "company": company,
            "position": position,
            "weak_areas": json.dumps(weak_areas) if weak_areas else "none"
        })
        
        try:
            questions = json.loads(response.content)
            logger.info(f"Generated {len(questions)} interview questions")
            return questions
        except json.JSONDecodeError:
            logger.warning("Failed to parse questions")
            return [
                {
                    "type": "technical",
                    "question": "Describe your experience with the technologies listed in the job posting",
                    "difficulty": "medium",
                    "topic": "general"
                }
            ]
    
    def create_study_plan(self, weak_areas: List[str], 
                         interview_date: str,
                         available_hours: int = 20) -> Dict[str, Any]:
        """Create personalized study plan"""
        logger.info("Creating study plan...")
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a study plan creator.
            Create a day-by-day study plan leading up to the interview.
            Prioritize weak areas and distribute time effectively.
            
            Return JSON:
            {{
                "total_hours": 20,
                "daily_schedule": [
                    {{
                        "day": 1,
                        "date": "2025-12-10",
                        "tasks": [
                            {{"topic": "System Design", "duration": 2, "resources": ["..."]}},
                            {{"topic": "Behavioral Prep", "duration": 1, "resources": ["..."]}}
                        ]
                    }}
                ],
                "priorities": ["System design", "..."],
                "resources": {{"books": [...], "videos": [...], "practice": [...]}}
            }}
            """),
            ("human", """Weak areas: {weak_areas}
Interview date: {interview_date}
Available hours: {available_hours}""")
        ])
        
        chain = prompt | self.llm
        response = chain.invoke({
            "weak_areas": json.dumps(weak_areas),
            "interview_date": interview_date,
            "available_hours": available_hours
        })
        
        try:
            plan = json.loads(response.content)
            logger.info(f"Created {len(plan.get('daily_schedule', []))}-day study plan")
            return plan
        except json.JSONDecodeError:
            logger.warning("Failed to parse study plan")
            return {
                "total_hours": available_hours,
                "daily_schedule": [],
                "priorities": weak_areas,
                "resources": {}
            }
    
    def find_practice_problems(self, topics: List[str], 
                              difficulty: str = "medium") -> List[Dict[str, Any]]:
        """Find relevant practice problems"""
        logger.info(f"Finding practice problems: {topics}")
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a coding practice expert.
            Suggest specific practice problems for these topics.
            Include problem name, platform (LeetCode/HackerRank), and difficulty.
            
            Return JSON array:
            [
                {{
                    "problem": "Two Sum",
                    "platform": "LeetCode",
                    "difficulty": "easy",
                    "topic": "arrays",
                    "url": "https://leetcode.com/problems/two-sum/",
                    "estimated_time": 30
                }}
            ]
            
            Provide 10-15 problems.
            """),
            ("human", "Topics: {topics}\nTarget difficulty: {difficulty}")
        ])
        
        chain = prompt | self.llm
        response = chain.invoke({
            "topics": json.dumps(topics),
            "difficulty": difficulty
        })
        
        try:
            problems = json.loads(response.content)
            logger.info(f"Found {len(problems)} practice problems")
            return problems
        except json.JSONDecodeError:
            logger.warning("Failed to parse practice problems")
            return []
    
    def compile_prep_guide(self, prep_data: Dict[str, Any]) -> str:
        """Compile comprehensive preparation guide"""
        logger.info("Compiling preparation guide...")
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an interview prep guide writer.
            Create a comprehensive, actionable preparation guide.
            
            Format:
            # Interview Preparation Guide
            ## Company: [Company]
            ## Position: [Position]
            ## Interview Date: [Date]
            
            ## 📊 Your Performance Analysis
            [Weak areas and patterns]
            
            ## ❓ Expected Questions
            [Categorized by type]
            
            ## 📅 Study Plan
            [Day-by-day schedule]
            
            ## 💻 Practice Problems
            [Curated problem list]
            
            ## 📚 Resources
            [Books, courses, articles]
            
            ## ✅ Pre-Interview Checklist
            [Final preparation steps]
            """),
            ("human", "Preparation data: {data}")
        ])
        
        chain = prompt | self.llm
        response = chain.invoke({"data": json.dumps(prep_data, indent=2)})
        
        guide = response.content
        logger.info("Preparation guide compiled")
        return guide
    
    def prepare(self, company: str, position: str, 
               interview_date: str, 
               available_hours: int = 20) -> Dict[str, Any]:
        """
        Run complete interview preparation workflow
        
        Args:
            company: Company name
            position: Job position
            interview_date: Interview date (YYYY-MM-DD)
            available_hours: Hours available for prep
        """
        task = f"Prepare for {position} interview at {company}"
        
        # Create custom initial state
        initial_state = self.create_initial_state(task)
        initial_state['prep_params'] = {
            'company': company,
            'position': position,
            'interview_date': interview_date,
            'available_hours': available_hours
        }
        
        result = self.run(task, prep_params={
            'company': company,
            'position': position,
            'interview_date': interview_date,
            'available_hours': available_hours
        })
        
        return result
    
    # Override think node for prep-specific planning
    def think_node(self, state: AgentState) -> AgentState:
        """Create interview prep-specific plan"""
        logger.info("Planning interview preparation...")
        
        params = state.get('prep_params', {})
        company = params.get('company', 'Unknown')
        position = params.get('position', 'Unknown')
        
        # Create comprehensive prep plan
        plan = [
            f"Search past applications for {company} or similar companies",
            "Analyze weaknesses from past rejections",
            f"Generate likely interview questions for {position}",
            "Find relevant practice problems",
            "Create personalized study plan",
            "Compile comprehensive preparation guide"
        ]
        
        state['plan'] = plan
        state['status'] = "executing"
        
        state['messages'].append({
            'role': 'assistant',
            'content': f"Interview prep plan created with {len(plan)} steps",
            'timestamp': datetime.now().isoformat()
        })
        
        return state
    
    def approve_and_execute(self, state: AgentState) -> Dict[str, Any]:
        """Compile and return preparation guide"""
        logger.info("Compiling final preparation guide...")
        
        # Extract all prep data
        prep_data = {
            'company': state.get('prep_params', {}).get('company'),
            'position': state.get('prep_params', {}).get('position'),
            'interview_date': state.get('prep_params', {}).get('interview_date'),
            'findings': {}
        }
        
        for obs in state.get('observations', []):
            tool = obs.get('tool')
            result = obs.get('result')
            
            if tool and result:
                prep_data['findings'][tool] = result
        
        # Generate final guide
        guide = self.compile_prep_guide(prep_data)
        
        return {
            'status': 'completed',
            'guide': guide,
            'data': prep_data,
            'timestamp': datetime.now().isoformat()
        }


# Example usage and testing
if __name__ == "__main__":
    # Test interview prep agent
    agent = InterviewPrepAgent()
    
    print("Running Interview Preparation Agent...")
    result = agent.prepare(
        company="Microsoft",
        position="Software Engineer",
        interview_date="2025-12-20",
        available_hours=25
    )
    
    print("\n=== Preparation Result ===")
    print(f"Status: {result.get('status')}")
    print(f"Steps completed: {len(result.get('observations', []))}")
    
    # Show observations
    print("\n=== Preparation Steps ===")
    for i, obs in enumerate(result.get('observations', []), 1):
        tool = obs.get('tool', 'unknown')
        print(f"{i}. {tool}: {obs.get('step')}")