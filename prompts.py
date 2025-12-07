"""
Centralized Prompt Templates for Job Tracker AI
Uses LangChain PromptTemplate for reusability and version control
"""

from langchain_core.prompts import PromptTemplate, ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from typing import Dict, List

# ==================== EXTRACTION PROMPTS ====================

JOB_EXTRACTION_TEMPLATE = """You are an expert at extracting job application information from emails.

{rag_context}

Extract job information from this email as valid JSON only:

Subject: {email_subject}
From: {email_from}
Body: {email_body}

Return this exact JSON format:
{{
  "company": "company name",
  "role": "job title",
  "status": "Applied|Interview|Assessment|Rejected|Offer|Other",
  "is_job_related": true/false
}}

Rules:
- company: Extract from sender or body{rag_hint}
- role: Job position title
- status: Applied if confirmation, Interview if scheduling, Rejected if "unfortunately", Other if unclear
- is_job_related: false only for spam/promotions

JSON:"""

job_extraction_prompt = PromptTemplate(
    input_variables=["rag_context", "email_subject", "email_from", "email_body", "rag_hint"],
    template=JOB_EXTRACTION_TEMPLATE
)

# ==================== ANALYSIS PROMPTS ====================

EMAIL_ANALYSIS_TEMPLATE = """You are an expert job application analyzer.

{rag_context}

=== NEW EMAIL TO ANALYZE ===
Subject: {email_subject}

Body:
{email_body}

=== TASK ===
Based on the email above{rag_similarity_hint}, provide:

1. **Status**: Categorize as one of: Applied, Interview, Offer, Rejection, Follow-up
2. **Company**: Extract company name
3. **Position**: Extract job title/position
4. **Key Information**:
   - Interview date/time (if mentioned)
   - Salary/compensation (if mentioned)
   - Next steps or deadlines
5. **Recommended Actions**: What should the user do next?
6. **Similarity Insights**: {similarity_context}

Format your response as valid JSON:
{{
  "status": "...",
  "company": "...",
  "position": "...",
  "key_info": "...",
  "recommended_actions": "...",
  "insights": "..."
}}
"""

email_analysis_prompt = PromptTemplate(
    input_variables=["rag_context", "email_subject", "email_body", "rag_similarity_hint", "similarity_context"],
    template=EMAIL_ANALYSIS_TEMPLATE
)

# ==================== AGENT PROMPTS (Phase 3) ====================

EMAIL_RESPONSE_AGENT_PROMPT = """You are an AI assistant that helps users respond to job-related emails professionally.

You have access to these tools:
- email_drafter: Drafts professional emails
- gmail_sender: Sends emails via Gmail API
- calendar_tool: Adds interview events to calendar
- template_selector: Chooses appropriate email template

Your task: Analyze this email and decide what action to take.

Email Subject: {email_subject}
Email Body: {email_body}
Email Type: {email_type}

Think step-by-step:
1. What type of email is this? (interview invite, rejection, offer, etc.)
2. Does it require a response?
3. What tools do I need to use?
4. What should the response contain?

Provide your reasoning and tool calls in JSON format.
"""

email_response_agent = PromptTemplate(
    input_variables=["email_subject", "email_body", "email_type"],
    template=EMAIL_RESPONSE_AGENT_PROMPT
)

COMPANY_RESEARCH_AGENT_PROMPT = """You are an AI research assistant that gathers information about companies for job applications.

You have access to these tools:
- web_search: Search the web for company information
- website_scraper: Extract content from company websites
- linkedin_search: Find employees and similar roles
- glassdoor_api: Get salary and review data
- report_generator: Format research findings

Your task: Research this company comprehensively.

Company: {company_name}
Position: {position}
User Background: {user_context}

Research Plan:
1. Company overview (mission, products, size, funding)
2. Recent news and developments
3. Company culture and values
4. Salary ranges for this role
5. Interview process insights
6. Key employees in relevant departments

Execute research step-by-step and compile a comprehensive report.
"""

company_research_agent = PromptTemplate(
    input_variables=["company_name", "position", "user_context"],
    template=COMPANY_RESEARCH_AGENT_PROMPT
)

INTERVIEW_PREP_AGENT_PROMPT = """You are an AI interview preparation assistant.

You have access to these tools:
- rag_search: Query past applications for patterns
- interview_db: Search common interview questions
- skills_analyzer: Identify skill gaps
- study_plan_generator: Create personalized study guides

Your task: Prepare the user for an upcoming interview.

Company: {company_name}
Position: {position}
User's Past Rejections: {rejection_patterns}
Job Requirements: {job_requirements}

Preparation Plan:
1. Analyze past rejections to identify weak areas
2. Find common interview questions for this role/company
3. Identify skill gaps vs. job requirements
4. Generate focused study plan with resources

Create a comprehensive interview preparation guide.
"""

interview_prep_agent = PromptTemplate(
    input_variables=["company_name", "position", "rejection_patterns", "job_requirements"],
    template=INTERVIEW_PREP_AGENT_PROMPT
)

# ==================== CHAIN-OF-THOUGHT PROMPTS (Phase 4) ====================

COT_EXTRACTION_TEMPLATE = """You are an expert at extracting job information from emails.
Think step-by-step through your reasoning before providing the answer.

Email Subject: {email_subject}
Email From: {email_from}
Email Body: {email_body}

Think through these steps:

Step 1: Is this email job-related?
Reasoning: [Explain why or why not]

Step 2: If job-related, what is the company name?
Reasoning: [How did you determine this? Where in the email?]

Step 3: What is the job role/position?
Reasoning: [Where did you find this information?]

Step 4: What is the application status?
Reasoning: [What keywords or context indicate the status?]

Step 5: Does this reasoning make sense? (Self-reflection)
Verification: [Check if your conclusions are consistent]

Final JSON Output:
{{
  "company": "...",
  "role": "...",
  "status": "...",
  "is_job_related": ...,
  "confidence": "high|medium|low",
  "reasoning_chain": ["step1 conclusion", "step2 conclusion", ...]
}}
"""

cot_extraction_prompt = PromptTemplate(
    input_variables=["email_subject", "email_from", "email_body"],
    template=COT_EXTRACTION_TEMPLATE
)

# ==================== FEW-SHOT EXAMPLES (Phase 4) ====================

FEW_SHOT_EXAMPLES = [
    {
        "email_subject": "Thank you for applying - Software Engineer at Google",
        "email_from": "Google Careers <noreply@google.com>",
        "email_body": "Dear Candidate, Thank you for your interest in the Software Engineer position at Google. We have received your application and our team will review it.",
        "expected_output": {
            "company": "Google",
            "role": "Software Engineer",
            "status": "Applied",
            "is_job_related": True
        }
    },
    {
        "email_subject": "Interview Invitation - Product Manager",
        "email_from": "Microsoft Recruiting <recruiting@microsoft.com>",
        "email_body": "Hi, We would like to schedule an interview for the Product Manager position. Are you available next Tuesday at 2 PM?",
        "expected_output": {
            "company": "Microsoft",
            "role": "Product Manager",
            "status": "Interview",
            "is_job_related": True
        }
    },
    {
        "email_subject": "Update on your application",
        "email_from": "Amazon Jobs <jobs@amazon.com>",
        "email_body": "Thank you for your interest. Unfortunately, we have decided to move forward with other candidates at this time.",
        "expected_output": {
            "company": "Amazon",
            "role": "Unknown",
            "status": "Rejected",
            "is_job_related": True
        }
    }
]

def build_few_shot_prompt(examples: List[Dict], new_email: Dict) -> str:
    """Build a few-shot prompt with examples"""
    prompt_parts = ["Here are some examples of correct email extraction:\n"]

    for i, example in enumerate(examples, 1):
        prompt_parts.append(f"""
Example {i}:
Subject: {example['email_subject']}
From: {example['email_from']}
Body: {example['email_body']}

Correct Output: {example['expected_output']}
---
""")

    prompt_parts.append(f"""
Now extract information from this NEW email:

Subject: {new_email['subject']}
From: {new_email['from']}
Body: {new_email['body']}

JSON Output:""")

    return "\n".join(prompt_parts)

# ==================== PROMPT VERSIONING ====================

PROMPT_VERSIONS = {
    "job_extraction": {
        "v1": JOB_EXTRACTION_TEMPLATE,
        "v2_cot": COT_EXTRACTION_TEMPLATE,
        "current": "v1"
    },
    "email_analysis": {
        "v1": EMAIL_ANALYSIS_TEMPLATE,
        "current": "v1"
    }
}

def get_prompt_version(prompt_name: str, version: str = None) -> PromptTemplate:
    """Get a specific version of a prompt, or the current version"""
    if prompt_name not in PROMPT_VERSIONS:
        raise ValueError(f"Unknown prompt: {prompt_name}")

    versions = PROMPT_VERSIONS[prompt_name]

    if version is None:
        version = versions["current"]

    if version not in versions:
        raise ValueError(f"Unknown version {version} for prompt {prompt_name}")

    template = versions[version]

    # Dynamically determine input variables from template
    return PromptTemplate.from_template(template)


# ==================== HELPER FUNCTIONS ====================

def format_rag_context(similar_apps: List[Dict]) -> str:
    """Format RAG context for prompt injection"""
    if not similar_apps:
        return "No similar past applications found."

    context_parts = ["=== CONTEXT: SIMILAR PAST APPLICATIONS ===\n"]
    for i, app in enumerate(similar_apps, 1):
        meta = app['metadata']
        context_parts.append(
            f"{i}. {meta['company']} - {meta['position']} "
            f"(Status: {meta['status']}, Similarity: {app['similarity']*100:.0f}%)\n"
        )
    context_parts.append("\nUse this context to improve extraction accuracy.\n")

    return "".join(context_parts)


def get_rag_hint(has_similar_apps: bool) -> str:
    """Get RAG hint for prompt"""
    if has_similar_apps:
        return " (refer to similar applications above if helpful)"
    return ""
