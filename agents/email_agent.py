"""
Email Response Agent
Autonomously drafts and sends professional email responses
"""

from typing import Dict, Any, Optional
from .base_agent import BaseAgent, AgentState
from langchain.prompts import ChatPromptTemplate
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class EmailResponseAgent(BaseAgent):
    """Agent for drafting and sending email responses"""
    
    def __init__(self, model_name: str = "llama3.2:3b", gmail_service=None):
        super().__init__(model_name=model_name, temperature=0.7)
        self.gmail_service = gmail_service
        self.email_templates = self._load_templates()
        
        # Register tools
        self.register_tool(
            "email_drafter",
            self.draft_email,
            "Draft professional email responses based on context"
        )
        self.register_tool(
            "template_selector",
            self.select_template,
            "Select appropriate email template for situation"
        )
        self.register_tool(
            "tone_analyzer",
            self.analyze_tone,
            "Analyze tone of incoming email to match response"
        )
        self.register_tool(
            "gmail_sender",
            self.send_email,
            "Send email via Gmail (requires approval)"
        )
        
        logger.info("EmailResponseAgent initialized")
    
    def _load_templates(self) -> Dict[str, str]:
        """Load email templates"""
        return {
            "interview_acceptance": """Dear {recruiter_name},

Thank you for the interview invitation for the {position} role at {company}. I am excited about this opportunity and would be delighted to attend.

I am available for the proposed time on {date} at {time}. Please let me know if you need any additional information before our meeting.

I look forward to speaking with you.

Best regards,
{candidate_name}""",
            
            "interview_decline": """Dear {recruiter_name},

Thank you for considering me for the {position} role at {company}. After careful consideration, I have decided to pursue other opportunities that align more closely with my career goals at this time.

I appreciate the time you invested in reviewing my application and wish you success in finding the right candidate.

Best regards,
{candidate_name}""",
            
            "follow_up": """Dear {recruiter_name},

I hope this email finds you well. I wanted to follow up on my application for the {position} role at {company}, which I submitted on {date}.

I remain very interested in this opportunity and would welcome the chance to discuss how my skills and experience align with your team's needs.

Thank you for your consideration.

Best regards,
{candidate_name}""",
            
            "thank_you": """Dear {recruiter_name},

Thank you for taking the time to speak with me about the {position} role at {company}. I enjoyed our conversation and learning more about {specific_topic}.

I am very excited about the possibility of joining your team and contributing to {company_goal}. Please don't hesitate to reach out if you need any additional information.

Looking forward to hearing from you.

Best regards,
{candidate_name}""",
            
            "status_inquiry": """Dear {recruiter_name},

I hope you're doing well. I wanted to check in regarding the status of my application for the {position} role at {company}.

I remain enthusiastic about this opportunity and would appreciate any updates you can share about the hiring timeline.

Thank you for your time.

Best regards,
{candidate_name}"""
        }
    
    def select_template(self, email_context: Dict[str, Any]) -> str:
        """Select appropriate email template"""
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an email classification expert.
            Analyze the context and determine the appropriate response type.
            
            Available templates:
            - interview_acceptance
            - interview_decline
            - follow_up
            - thank_you
            - status_inquiry
            
            Return JSON: {{"template": "template_name", "reason": "explanation"}}
            """),
            ("human", "Email context: {context}")
        ])
        
        chain = prompt | self.llm
        response = chain.invoke({"context": json.dumps(email_context)})
        
        try:
            result = json.loads(response.content)
            template_name = result.get('template', 'follow_up')
            logger.info(f"Selected template: {template_name}")
            return template_name
        except json.JSONDecodeError:
            logger.warning("Failed to parse template selection, using default")
            return "follow_up"
    
    def analyze_tone(self, email_body: str) -> Dict[str, Any]:
        """Analyze tone of incoming email"""
        prompt = ChatPromptTemplate.from_messages([
            ("system", """Analyze the tone of this email.
            Return JSON: {{"tone": "formal/casual/enthusiastic", "urgency": "high/medium/low", "sentiment": "positive/neutral/negative"}}
            """),
            ("human", "Email: {email}")
        ])
        
        chain = prompt | self.llm
        response = chain.invoke({"email": email_body})
        
        try:
            analysis = json.loads(response.content)
            logger.info(f"Tone analysis: {analysis}")
            return analysis
        except json.JSONDecodeError:
            return {"tone": "formal", "urgency": "medium", "sentiment": "neutral"}
    
    def draft_email(self, template_name: str = None, **context) -> str:
        """Draft email using template or AI generation"""
        if template_name and template_name in self.email_templates:
            # Use template
            template = self.email_templates[template_name]
            try:
                draft = template.format(**context)
                logger.info(f"Drafted email using template: {template_name}")
                return draft
            except KeyError as e:
                logger.warning(f"Missing template variable: {e}")
        
        # AI-generated draft
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a professional email writer.
            Draft a professional, concise email response based on the context.
            Match the tone of the incoming email.
            Keep it under 150 words.
            """),
            ("human", "Context: {context}\n\nDraft the email:")
        ])
        
        chain = prompt | self.llm
        response = chain.invoke({"context": json.dumps(context)})
        
        draft = response.content.strip()
        logger.info("Drafted AI-generated email")
        return draft
    
    def send_email(self, to: str, subject: str, body: str, 
                   cc: Optional[str] = None) -> Dict[str, Any]:
        """Send email via Gmail API"""
        if not self.gmail_service:
            logger.warning("Gmail service not configured")
            return {
                'success': False,
                'error': 'Gmail service not configured',
                'draft': body
            }
        
        try:
            # This would integrate with actual Gmail API
            # Placeholder for now
            logger.info(f"Email sent to {to}")
            return {
                'success': True,
                'to': to,
                'subject': subject,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return {
                'success': False,
                'error': str(e),
                'draft': body
            }
    
    def run_email_workflow(self, email_data: Dict[str, Any], 
                          action: str = "draft") -> Dict[str, Any]:
        """
        Run complete email workflow
        
        Args:
            email_data: Contains subject, body, from, etc.
            action: 'draft', 'send', 'analyze'
        """
        task = f"{action} response to: {email_data.get('subject', 'email')}"
        
        # Add email context to state
        initial_state = self.create_initial_state(task)
        initial_state['email_data'] = email_data
        initial_state['action'] = action
        
        # Build custom workflow for email
        result = self.run(task, email_data=email_data, action=action)
        
        return result
    
    # Override think node for email-specific planning
    def think_node(self, state: AgentState) -> AgentState:
        """Create email-specific plan"""
        logger.info("Planning email response...")
        
        email_data = state.get('email_data', {})
        action = state.get('action', 'draft')
        
        # Create plan based on action
        if action == "draft":
            state['plan'] = [
                "Analyze tone of incoming email",
                "Select appropriate email template",
                "Draft email response",
                "Review and format"
            ]
        elif action == "send":
            state['plan'] = [
                "Analyze tone of incoming email",
                "Select appropriate email template",
                "Draft email response",
                "Send via Gmail"
            ]
        else:  # analyze
            state['plan'] = [
                "Analyze tone of incoming email",
                "Extract key information",
                "Provide response recommendations"
            ]
        
        state['status'] = "executing"
        state['messages'].append({
            'role': 'assistant',
            'content': f"Email plan created: {state['plan']}",
            'timestamp': datetime.now().isoformat()
        })
        
        return state
    
    def approve_and_execute(self, state: AgentState) -> Dict[str, Any]:
        """Execute approved email sending"""
        logger.info("Executing approved email...")
        
        if not state.get('approved'):
            return {'error': 'Email not approved'}
        
        # Extract draft from observations
        draft = None
        for obs in state['observations']:
            if obs.get('tool') == 'email_drafter':
                draft = obs.get('result')
                break
        
        if not draft:
            return {'error': 'No draft found'}
        
        email_data = state.get('email_data', {})
        
        # Send email
        result = self.send_email(
            to=email_data.get('from'),
            subject=f"Re: {email_data.get('subject')}",
            body=draft
        )
        
        return {
            'status': 'executed',
            'result': result,
            'draft': draft
        }


# Example usage and testing
if __name__ == "__main__":
    # Test email agent
    agent = EmailResponseAgent()
    
    # Sample incoming email
    test_email = {
        'from': 'recruiter@company.com',
        'subject': 'Interview Invitation - Software Engineer',
        'body': """Hi there,

We were impressed with your application and would like to invite you for an interview for the Software Engineer position.

Would you be available next Tuesday at 2 PM for a virtual interview?

Best regards,
Jane Doe
Senior Recruiter""",
        'received_date': '2025-12-01'
    }
    
    # Draft response
    print("Running Email Response Agent...")
    result = agent.run_email_workflow(test_email, action="draft")
    
    print("\n=== Agent Result ===")
    print(f"Status: {result.get('status')}")
    print(f"Observations: {len(result.get('observations', []))}")
    
    # Print draft if available
    for obs in result.get('observations', []):
        if obs.get('tool') == 'email_drafter':
            print(f"\n=== Draft Email ===")
            print(obs.get('result'))