"""
Unit Tests for AI Agents
Test all three agents and their tools
"""

import unittest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agents import EmailResponseAgent, CompanyResearchAgent, InterviewPrepAgent
from agents.base_agent import AgentState


class TestEmailResponseAgent(unittest.TestCase):
    """Test Email Response Agent"""
    
    def setUp(self):
        """Initialize agent for testing"""
        self.agent = EmailResponseAgent()
    
    def test_agent_initialization(self):
        """Test agent initializes correctly"""
        self.assertIsNotNone(self.agent)
        self.assertEqual(len(self.agent.tools), 4)
        self.assertIn('email_drafter', self.agent.tools)
    
    def test_template_selection(self):
        """Test email template selection"""
        context = {
            'subject': 'Interview Invitation - Software Engineer',
            'body': 'We would like to invite you for an interview...'
        }
        template = self.agent.select_template(context)
        self.assertIsInstance(template, str)
        self.assertIn(template, self.agent.email_templates.keys())
    
    def test_tone_analysis(self):
        """Test email tone analysis"""
        email = "Dear Candidate, We are excited to invite you for an interview!"
        analysis = self.agent.analyze_tone(email)
        
        self.assertIsInstance(analysis, dict)
        self.assertIn('tone', analysis)
        self.assertIn('urgency', analysis)
        self.assertIn('sentiment', analysis)
    
    def test_draft_email_with_template(self):
        """Test email drafting with template"""
        draft = self.agent.draft_email(
            template_name='interview_acceptance',
            recruiter_name='Jane Doe',
            position='Software Engineer',
            company='Google',
            date='December 20, 2025',
            time='2:00 PM',
            candidate_name='John Smith'
        )
        
        self.assertIsInstance(draft, str)
        self.assertIn('Jane Doe', draft)
        self.assertIn('Google', draft)
    
    def test_email_workflow(self):
        """Test complete email workflow"""
        email_data = {
            'from': 'recruiter@company.com',
            'subject': 'Interview Invitation',
            'body': 'We would like to schedule an interview...',
            'received_date': '2025-12-01'
        }
        
        result = self.agent.run_email_workflow(email_data, action='draft')
        
        self.assertIsInstance(result, dict)
        self.assertIn('status', result)
        self.assertIn('observations', result)


class TestCompanyResearchAgent(unittest.TestCase):
    """Test Company Research Agent"""
    
    def setUp(self):
        """Initialize agent for testing"""
        self.agent = CompanyResearchAgent()
    
    def test_agent_initialization(self):
        """Test agent initializes correctly"""
        self.assertIsNotNone(self.agent)
        self.assertEqual(len(self.agent.tools), 6)
        self.assertIn('web_search', self.agent.tools)
    
    def test_web_search(self):
        """Test web search tool"""
        results = self.agent.web_search("Google company information")
        
        self.assertIsInstance(results, list)
        if results:
            self.assertIn('title', results[0])
            self.assertIn('url', results[0])
    
    def test_salary_lookup(self):
        """Test salary lookup"""
        salary_data = self.agent.lookup_salary(
            company="Google",
            position="Software Engineer",
            location="Mountain View, CA"
        )
        
        self.assertIsInstance(salary_data, dict)
        self.assertIn('min', salary_data)
        self.assertIn('max', salary_data)
        self.assertIn('currency', salary_data)
    
    def test_culture_analysis(self):
        """Test company culture analysis"""
        culture_data = self.agent.analyze_culture("Google")
        
        self.assertIsInstance(culture_data, dict)
        self.assertIn('work_life_balance', culture_data)
        self.assertIn('management', culture_data)
        self.assertIn('overall_rating', culture_data)
    
    def test_research_workflow(self):
        """Test complete research workflow"""
        result = self.agent.research(
            company="Microsoft",
            position="Product Manager",
            location="Seattle, WA"
        )
        
        self.assertIsInstance(result, dict)
        self.assertIn('status', result)
        self.assertIn('observations', result)


class TestInterviewPrepAgent(unittest.TestCase):
    """Test Interview Preparation Agent"""
    
    def setUp(self):
        """Initialize agent for testing"""
        self.agent = InterviewPrepAgent()
    
    def test_agent_initialization(self):
        """Test agent initializes correctly"""
        self.assertIsNotNone(self.agent)
        self.assertEqual(len(self.agent.tools), 6)
        self.assertIn('question_generator', self.agent.tools)
    
    def test_weakness_analysis(self):
        """Test weakness analysis from past applications"""
        past_apps = [
            {
                'company': 'Google',
                'position': 'SWE',
                'status': 'rejected',
                'notes': 'Failed at system design'
            },
            {
                'company': 'Facebook',
                'position': 'SWE',
                'status': 'rejected',
                'notes': 'Weak on algorithms'
            }
        ]
        
        analysis = self.agent.analyze_weaknesses(past_apps)
        
        self.assertIsInstance(analysis, dict)
        self.assertIn('weak_areas', analysis)
        self.assertIn('recommendations', analysis)
    
    def test_question_generation(self):
        """Test interview question generation"""
        questions = self.agent.generate_questions(
            company="Amazon",
            position="Software Engineer",
            weak_areas=["system design", "algorithms"]
        )
        
        self.assertIsInstance(questions, list)
        if questions:
            self.assertIn('type', questions[0])
            self.assertIn('question', questions[0])
            self.assertIn('difficulty', questions[0])
    
    def test_study_plan_creation(self):
        """Test study plan creation"""
        plan = self.agent.create_study_plan(
            weak_areas=["system design", "behavioral"],
            interview_date="2025-12-20",
            available_hours=20
        )
        
        self.assertIsInstance(plan, dict)
        self.assertIn('daily_schedule', plan)
        self.assertIn('priorities', plan)
    
    def test_practice_problems(self):
        """Test practice problem finder"""
        problems = self.agent.find_practice_problems(
            topics=["arrays", "trees", "graphs"],
            difficulty="medium"
        )
        
        self.assertIsInstance(problems, list)
        if problems:
            self.assertIn('problem', problems[0])
            self.assertIn('platform', problems[0])
    
    def test_prep_workflow(self):
        """Test complete prep workflow"""
        result = self.agent.prepare(
            company="Apple",
            position="Software Engineer",
            interview_date="2025-12-25",
            available_hours=25
        )
        
        self.assertIsInstance(result, dict)
        self.assertIn('status', result)
        self.assertIn('observations', result)


class TestBaseAgent(unittest.TestCase):
    """Test Base Agent functionality"""
    
    def setUp(self):
        """Initialize base agent"""
        from agents.base_agent import BaseAgent
        self.agent = BaseAgent()
    
    def test_tool_registration(self):
        """Test tool registration"""
        def dummy_tool(x):
            return x * 2
        
        self.agent.register_tool(
            name="dummy",
            func=dummy_tool,
            description="A dummy tool"
        )
        
        self.assertIn('dummy', self.agent.tools)
        self.assertEqual(self.agent.tools['dummy']['function'](5), 10)
    
    def test_state_creation(self):
        """Test agent state creation"""
        state = self.agent.create_initial_state("Test task")
        
        self.assertIsInstance(state, dict)
        self.assertEqual(state['current_task'], "Test task")
        self.assertEqual(state['status'], "planning")
        self.assertEqual(state['iterations'], 0)
    
    def test_graph_building(self):
        """Test graph compilation"""
        graph = self.agent.build_graph()
        
        self.assertIsNotNone(graph)
        self.assertIsNotNone(self.agent.graph)


class TestAgentIntegration(unittest.TestCase):
    """Integration tests for agents working together"""
    
    def test_multi_agent_workflow(self):
        """Test multiple agents in sequence"""
        # Research company
        research_agent = CompanyResearchAgent()
        research_result = research_agent.research(
            company="Stripe",
            position="Backend Engineer"
        )
        
        self.assertIn('status', research_result)
        
        # Prepare for interview
        interview_agent = InterviewPrepAgent()
        prep_result = interview_agent.prepare(
            company="Stripe",
            position="Backend Engineer",
            interview_date="2025-12-30",
            available_hours=15
        )
        
        self.assertIn('status', prep_result)
        
        # Draft thank you email
        email_agent = EmailResponseAgent()
        email_data = {
            'from': 'recruiter@stripe.com',
            'subject': 'Thanks for the interview',
            'body': 'It was great speaking with you...',
            'received_date': '2025-12-30'
        }
        
        email_result = email_agent.run_email_workflow(
            email_data,
            action='draft'
        )
        
        self.assertIn('status', email_result)


def run_tests():
    """Run all tests"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestEmailResponseAgent))
    suite.addTests(loader.loadTestsFromTestCase(TestCompanyResearchAgent))
    suite.addTests(loader.loadTestsFromTestCase(TestInterviewPrepAgent))
    suite.addTests(loader.loadTestsFromTestCase(TestBaseAgent))
    suite.addTests(loader.loadTestsFromTestCase(TestAgentIntegration))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)