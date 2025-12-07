"""
Tools for AI Agents
Functions that agents can use to take actions
"""

from typing import Dict, List, Optional
import requests
from datetime import datetime

# ==================== EMAIL TOOLS ====================

def draft_email(email_type: str, context: Dict) -> str:
    """
    Draft a professional email

    Args:
        email_type: "acceptance", "decline", "follow_up", "thank_you"
        context: Dictionary with email context (company, position, etc.)

    Returns:
        Drafted email text
    """

    templates = {
        "acceptance": """
Dear {recruiter},

Thank you for the interview invitation for the {position} role at {company}.
I am excited about this opportunity and would be delighted to speak with you.

I am available on {date} at {time}. Please let me know if this works for you.

Looking forward to our conversation.

Best regards,
{name}
""",
        "decline": """
Dear {recruiter},

Thank you for considering me for the {position} role at {company}.
After careful consideration, I have decided to pursue other opportunities
that align more closely with my current career goals.

I appreciate your time and wish you success in finding the right candidate.

Best regards,
{name}
""",
        "follow_up": """
Dear {recruiter},

I hope this email finds you well. I wanted to follow up on my application
for the {position} role at {company} submitted on {date}.

I remain very interested in this opportunity and would appreciate any updates
you can share regarding the status of my application.

Thank you for your time and consideration.

Best regards,
{name}
""",
        "thank_you": """
Dear {interviewer},

Thank you for taking the time to speak with me about the {position} role
at {company}. I enjoyed our conversation and learning more about the team
and the exciting work you're doing.

I am very enthusiastic about the opportunity to contribute to {company}
and look forward to hearing about the next steps.

Best regards,
{name}
"""
    }

    template = templates.get(email_type, templates["follow_up"])
    return template.format(**context)


def send_email_via_gmail(to: str, subject: str, body: str) -> bool:
    """
    Send email via Gmail API

    Args:
        to: Recipient email
        subject: Email subject
        body: Email body

    Returns:
        True if sent successfully
    """
    # TODO: Implement Gmail API integration
    # from email_fetcher import get_gmail_service
    # service = get_gmail_service()
    # message = create_message('me', to, subject, body)
    # service.users().messages().send(userId='me', body=message).execute()

    print(f"[MOCK] Sending email to {to}: {subject}")
    return True


def add_to_calendar(event_title: str, event_date: str, event_time: str, duration_mins: int = 60) -> bool:
    """
    Add event to Google Calendar

    Args:
        event_title: Event title
        event_date: Date (YYYY-MM-DD)
        event_time: Time (HH:MM)
        duration_mins: Duration in minutes

    Returns:
        True if added successfully
    """
    # TODO: Implement Google Calendar API integration

    print(f"[MOCK] Adding to calendar: {event_title} on {event_date} at {event_time}")
    return True


# ==================== RESEARCH TOOLS ====================

def web_search(query: str, num_results: int = 5) -> List[Dict]:
    """
    Search the web

    Args:
        query: Search query
        num_results: Number of results to return

    Returns:
        List of search results with title, url, snippet
    """
    # TODO: Implement with Google Custom Search API or alternative

    print(f"[MOCK] Searching web for: {query}")
    return [
        {
            "title": f"Result {i} for {query}",
            "url": f"https://example.com/{i}",
            "snippet": f"Mock snippet for {query}..."
        }
        for i in range(num_results)
    ]


def scrape_website(url: str) -> str:
    """
    Extract text content from a website

    Args:
        url: Website URL

    Returns:
        Extracted text content
    """
    # TODO: Implement with BeautifulSoup or similar

    try:
        response = requests.get(url, timeout=10)
        # In real implementation: parse HTML and extract text
        print(f"[MOCK] Scraping {url}")
        return f"Mock content from {url}"
    except Exception as e:
        return f"Error scraping {url}: {e}"


def search_linkedin(company: str, position: str) -> List[Dict]:
    """
    Search LinkedIn for people in similar roles

    Args:
        company: Company name
        position: Position title

    Returns:
        List of LinkedIn profiles
    """
    # TODO: Implement LinkedIn API or scraping (be careful with ToS)

    print(f"[MOCK] Searching LinkedIn: {position} at {company}")
    return [
        {
            "name": "John Doe",
            "title": position,
            "company": company,
            "profile_url": "https://linkedin.com/in/johndoe"
        }
    ]


def get_glassdoor_data(company: str) -> Dict:
    """
    Get Glassdoor ratings and salary data

    Args:
        company: Company name

    Returns:
        Dictionary with rating, salary range, reviews
    """
    # TODO: Implement Glassdoor API

    print(f"[MOCK] Getting Glassdoor data for {company}")
    return {
        "rating": 4.2,
        "salary_range": "$100k - $150k",
        "pros": "Great work-life balance, innovative culture",
        "cons": "Fast-paced environment",
        "interview_difficulty": "Medium"
    }


# ==================== INTERVIEW PREP TOOLS ====================

def search_interview_questions(company: str, position: str) -> List[str]:
    """
    Search for common interview questions

    Args:
        company: Company name
        position: Position title

    Returns:
        List of common interview questions
    """
    # TODO: Implement with interview question database

    print(f"[MOCK] Searching interview questions: {position} at {company}")
    return [
        "Tell me about yourself",
        f"Why do you want to work at {company}?",
        f"What interests you about the {position} role?",
        "Describe a challenging project you worked on",
        "How do you handle conflict in a team?"
    ]


def analyze_skills_gap(job_requirements: List[str], user_skills: List[str]) -> Dict:
    """
    Identify skill gaps

    Args:
        job_requirements: Required skills
        user_skills: User's current skills

    Returns:
        Dictionary with matching skills, missing skills, learning resources
    """
    job_set = set(job_requirements)
    user_set = set(user_skills)

    matching = list(job_set & user_set)
    missing = list(job_set - user_set)

    return {
        "matching_skills": matching,
        "missing_skills": missing,
        "match_percentage": len(matching) / len(job_set) * 100 if job_set else 0,
        "learning_resources": [f"Learn {skill}" for skill in missing]
    }


def generate_study_plan(weak_areas: List[str], days_until_interview: int) -> Dict:
    """
    Generate a study plan

    Args:
        weak_areas: Topics to focus on
        days_until_interview: Days until interview

    Returns:
        Structured study plan
    """
    hours_per_day = min(3, max(1, 10 / days_until_interview))

    plan = {
        "total_days": days_until_interview,
        "hours_per_day": hours_per_day,
        "schedule": []
    }

    for i, topic in enumerate(weak_areas):
        day = (i % days_until_interview) + 1
        plan["schedule"].append({
            "day": day,
            "topic": topic,
            "hours": hours_per_day / len(weak_areas),
            "activities": [
                f"Review {topic} fundamentals",
                f"Practice {topic} problems",
                f"Mock interview on {topic}"
            ]
        })

    return plan


# ==================== RAG SEARCH TOOL ====================

def rag_search_tool(query: str, rag_engine, top_k: int = 3) -> List[Dict]:
    """
    Search RAG for similar past applications

    Args:
        query: Search query
        rag_engine: RAG engine instance
        top_k: Number of results

    Returns:
        List of similar applications
    """
    if rag_engine:
        return rag_engine.search_similar_applications(query, top_k=top_k)
    return []


# ==================== REPORT GENERATION ====================

def generate_research_report(company: str, research_data: Dict) -> str:
    """
    Format research findings into a report

    Args:
        company: Company name
        research_data: Collected research data

    Returns:
        Formatted markdown report
    """
    report = f"""# Company Research Report: {company}

## Overview
{research_data.get('overview', 'No overview available')}

## Recent News
{research_data.get('news', 'No recent news found')}

## Company Culture
- **Rating:** {research_data.get('glassdoor', {}).get('rating', 'N/A')}
- **Pros:** {research_data.get('glassdoor', {}).get('pros', 'N/A')}
- **Cons:** {research_data.get('glassdoor', {}).get('cons', 'N/A')}

## Salary Information
{research_data.get('glassdoor', {}).get('salary_range', 'N/A')}

## Interview Insights
- **Difficulty:** {research_data.get('glassdoor', {}).get('interview_difficulty', 'Unknown')}
- **Common Questions:** See interview prep section

## Recommendations
Based on this research:
1. Focus on {company}'s core values
2. Prepare examples demonstrating relevant skills
3. Research recent company initiatives

---
*Report generated on {datetime.now().strftime('%Y-%m-%d')}*
"""
    return report


# ==================== TOOL REGISTRY ====================

# Tools available to agents
AGENT_TOOLS = {
    # Email tools
    "draft_email": draft_email,
    "send_email": send_email_via_gmail,
    "add_to_calendar": add_to_calendar,

    # Research tools
    "web_search": web_search,
    "scrape_website": scrape_website,
    "search_linkedin": search_linkedin,
    "get_glassdoor_data": get_glassdoor_data,

    # Interview prep tools
    "search_interview_questions": search_interview_questions,
    "analyze_skills_gap": analyze_skills_gap,
    "generate_study_plan": generate_study_plan,

    # RAG tool
    "rag_search": rag_search_tool,

    # Report generation
    "generate_report": generate_research_report
}
