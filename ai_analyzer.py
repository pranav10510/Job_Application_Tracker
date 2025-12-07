"""
AI Analyzer with LangChain Integration
Extracts job information from emails using Ollama + LangChain
"""

import requests
import json
import re
from typing import Optional, Dict
from config import (
    USE_RAG,
    USE_LANGCHAIN,
    LANGCHAIN_MODE,
    OLLAMA_MODEL,
    OLLAMA_BASE_URL,
    OLLAMA_TIMEOUT
)

OLLAMA_API_URL = f"{OLLAMA_BASE_URL}/api/generate"
MODEL_NAME = OLLAMA_MODEL

# ==================== LEGACY IMPLEMENTATION (Fallback) ====================

def call_ollama(prompt):
    """Call Ollama API directly (legacy method)"""
    try:
        response = requests.post(
            OLLAMA_API_URL,
            json={
                "model": MODEL_NAME,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.1,
                    "num_predict": 200
                }
            },
            timeout=OLLAMA_TIMEOUT
        )

        if response.status_code == 200:
            result = response.json()
            return result.get('response', '').strip()
        else:
            print(f"❌ Ollama API error: {response.status_code}")
            return None

    except requests.exceptions.ConnectionError:
        print(f"❌ Cannot connect to Ollama at {OLLAMA_API_URL}")
        return None
    except requests.exceptions.Timeout:
        print("❌ Ollama API timeout")
        return None
    except Exception as e:
        print(f"❌ Error calling Ollama: {e}")
        return None


def extract_job_info_legacy(email_data, rag_engine=None):
    """Legacy extraction method (kept for fallback)"""

    subject = email_data.get('subject', '')
    sender = email_data.get('from', '')
    body = email_data.get('body', '')[:2000]

    # RAG context
    rag_context = ""
    similar_apps = []

    if USE_RAG and rag_engine is not None:
        try:
            search_query = f"{subject}\n\n{body[:500]}"
            similar_apps = rag_engine.search_similar_applications(
                query_text=search_query,
                top_k=3
            )

            if similar_apps:
                rag_context = "\n=== CONTEXT: SIMILAR PAST APPLICATIONS ===\n"
                for i, app in enumerate(similar_apps, 1):
                    meta = app['metadata']
                    rag_context += f"{i}. {meta['company']} - {meta['position']} (Status: {meta['status']}, Similarity: {app['similarity']*100:.0f}%)\n"
                rag_context += "\nUse this context to improve extraction accuracy.\n"
                print(f"  ✓ RAG: Found {len(similar_apps)} similar applications")
        except Exception as e:
            print(f"  ⚠️ RAG search failed: {e}")
            rag_context = ""

    # Build prompt
    prompt = f"""{rag_context}

Extract job info from this email as JSON only:

Subject: {subject}
From: {sender}
Body: {body}

Return this exact format:
{{"company": "name", "role": "title", "status": "Applied|Interview|Assessment|Rejected|Offer|Other", "is_job_related": true}}

Rules:
- company: extract from sender or body{' (refer to similar applications above if helpful)' if rag_context else ''}
- role: job position title
- status: Applied if confirmation, Interview if scheduling, Rejected if "unfortunately", Other if unclear
- is_job_related: false only for spam/promotions

JSON:"""

    response = call_ollama(prompt)

    if not response:
        return None

    try:
        # Parse JSON
        response = re.sub(r'```json\n?|\n?```', '', response)
        response = response.strip()

        json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', response, re.DOTALL)
        if json_match:
            response = json_match.group()

        data = json.loads(response)

        # Add metadata
        data['email_subject'] = subject
        data['email_from'] = sender
        data['email_date'] = email_data.get('date', '')
        data['email_body'] = body
        data['rag_used'] = USE_RAG and len(similar_apps) > 0
        data['similar_count'] = len(similar_apps)

        return data

    except json.JSONDecodeError as e:
        print(f"JSON parse error: {response[:150]}")
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None


# ==================== LANGCHAIN IMPLEMENTATION ====================

_chain_factory = None

def get_chain_factory(rag_engine=None):
    """Get or create ChainFactory singleton"""
    global _chain_factory

    if USE_LANGCHAIN:
        try:
            from chains import ChainFactory
            if _chain_factory is None:
                _chain_factory = ChainFactory(rag_engine=rag_engine)
            elif rag_engine is not None and _chain_factory.rag_engine is None:
                # Update RAG engine if it wasn't set initially
                _chain_factory.rag_engine = rag_engine
            return _chain_factory
        except ImportError as e:
            print(f"⚠️ LangChain import failed: {e}")
            print("   Falling back to legacy implementation")
            return None
    return None


def extract_job_info(email_data, rag_engine=None):
    """
    Extract job info using LangChain (or legacy if disabled)

    Args:
        email_data: Dictionary with email details
        rag_engine: Pre-initialized RAG engine (optional)

    Returns:
        Dictionary with extracted job information
    """

    # Try LangChain first if enabled
    if USE_LANGCHAIN:
        try:
            factory = get_chain_factory(rag_engine)
            if factory:
                chain = factory.get_extraction_chain(mode=LANGCHAIN_MODE)
                result = chain.invoke(email_data)

                # Add metadata if not present
                if isinstance(result, dict) and "error" not in result:
                    result.setdefault('email_subject', email_data.get('subject', ''))
                    result.setdefault('email_from', email_data.get('from', ''))
                    result.setdefault('email_date', email_data.get('date', ''))
                    result.setdefault('email_body', email_data.get('body', '')[:2000])

                print(f"  ✓ LangChain extraction successful (mode: {LANGCHAIN_MODE})")
                return result

        except Exception as e:
            print(f"  ⚠️ LangChain extraction failed: {e}")
            print("     Falling back to legacy method...")

    # Fallback to legacy
    return extract_job_info_legacy(email_data, rag_engine)


def analyze_with_ollama(email_subject: str,
                        email_body: str,
                        app_id: Optional[str] = None,
                        rag_engine=None) -> Dict:
    """
    Analyze email with optional RAG context (LangChain-powered)

    Args:
        email_subject: Email subject line
        email_body: Email body text
        app_id: Optional application ID (to exclude from RAG search)
        rag_engine: Optional RAG engine

    Returns:
        Dictionary with analysis results
    """

    email_data = {
        'subject': email_subject,
        'body': email_body,
        'id': app_id
    }

    # Try LangChain analysis if enabled
    if USE_LANGCHAIN:
        try:
            factory = get_chain_factory(rag_engine)
            if factory:
                chain = factory.get_analysis_chain()
                result = chain.invoke(email_data)
                print("  ✓ LangChain analysis successful")
                return result
        except Exception as e:
            print(f"  ⚠️ LangChain analysis failed: {e}")
            print("     Falling back to legacy analysis...")

    # Legacy fallback
    return analyze_with_ollama_legacy(email_subject, email_body, app_id, rag_engine)


def analyze_with_ollama_legacy(email_subject: str,
                                email_body: str,
                                app_id: Optional[str] = None,
                                rag_engine=None) -> Dict:
    """Legacy analysis method"""

    rag_context = ""
    similar_apps = []

    if USE_RAG and rag_engine:
        try:
            search_query = f"{email_subject}\n\n{email_body[:500]}"
            similar_apps = rag_engine.search_similar_applications(
                query_text=search_query,
                exclude_id=app_id,
                top_k=3
            )

            if similar_apps:
                rag_context = "\n=== SIMILAR PAST APPLICATIONS ===\n"
                for i, app in enumerate(similar_apps, 1):
                    meta = app['metadata']
                    rag_context += f"{i}. {meta['company']} - {meta['position']} (Similarity: {app['similarity']*100:.0f}%)\n"
                print(f"✓ RAG: Found {len(similar_apps)} similar applications")
        except Exception as e:
            print(f"⚠ RAG error: {e}")
            rag_context = ""

    prompt = f"""
{rag_context}

=== NEW EMAIL TO ANALYZE ===
Subject: {email_subject}
Body: {email_body}

Based on the email above, provide:
1. **Status**: Applied, Interview, Offer, Rejection, or Follow-up
2. **Company**: Company name
3. **Position**: Job title
4. **Key Information**: Important details (interview times, deadlines, etc.)
5. **Recommended Actions**: What to do next
6. **Insights**: Patterns from similar applications

Format as valid JSON:
{{
  "status": "...",
  "company": "...",
  "position": "...",
  "key_info": "...",
  "recommended_actions": "...",
  "insights": "..."
}}
"""

    try:
        response = requests.post(
            OLLAMA_API_URL,
            json={
                "model": MODEL_NAME,
                "prompt": prompt,
                "stream": False,
                "temperature": 0.3
            },
            timeout=120
        )

        if response.status_code == 200:
            result = response.json()
            analysis_text = result.get('response', '')

            # Parse JSON
            if '```json' in analysis_text:
                json_start = analysis_text.find('```json') + 7
                json_end = analysis_text.find('```', json_start)
                analysis_text = analysis_text[json_start:json_end]

            analysis = json.loads(analysis_text.strip())
            analysis['rag_used'] = USE_RAG and len(similar_apps) > 0
            analysis['similar_count'] = len(similar_apps)

            return analysis

        else:
            raise Exception(f"Ollama API error: {response.status_code}")

    except Exception as e:
        print(f"Error analyzing with Ollama: {e}")
        return {
            "status": "Error",
            "company": "Unknown",
            "position": "Unknown",
            "error": str(e)
        }


# ==================== TESTING ====================

if __name__ == "__main__":
    print("=" * 70)
    print("AI ANALYZER TEST - LangChain Integration")
    print("=" * 70)

    # Check Ollama
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            print("\n✓ Ollama running")
        else:
            print("\n❌ Ollama not responding")
            exit(1)
    except:
        print("\n❌ Ollama not running!")
        exit(1)

    # Check LangChain
    print(f"\nLangChain Mode: {'ENABLED' if USE_LANGCHAIN else 'DISABLED'}")
    if USE_LANGCHAIN:
        print(f"Chain Mode: {LANGCHAIN_MODE}")

    # Test emails
    test_emails = [
        {
            'subject': 'Thank you for applying to Software Engineer at Google',
            'from': 'Google Careers <noreply@google.com>',
            'body': 'Dear Candidate, Thank you for your interest in the Software Engineer position at Google.',
            'date': '2025-10-20'
        },
        {
            'subject': 'Interview Invitation - Product Manager Role',
            'from': 'Microsoft Recruiting <recruiting@microsoft.com>',
            'body': 'Hi, We would like to schedule an interview for the Product Manager position. Are you available next week?',
            'date': '2025-10-21'
        }
    ]

    print("\n" + "=" * 70)
    print("Testing extraction...")
    print("=" * 70 + "\n")

    for i, test_email in enumerate(test_emails, 1):
        print(f"--- Test {i} ---")
        print(f"Subject: {test_email['subject']}")

        result = extract_job_info(test_email)

        if result:
            print(f"✓ Company: {result.get('company')}")
            print(f"✓ Role: {result.get('role')}")
            print(f"✓ Status: {result.get('status')}")
            print(f"✓ Job Related: {result.get('is_job_related')}\n")
        else:
            print(f"❌ Failed\n")

    print("=" * 70)
    print("Tests complete!")
    print("=" * 70)
