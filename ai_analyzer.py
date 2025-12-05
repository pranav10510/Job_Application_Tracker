import requests
import json
import re
from typing import Optional, Dict
from config import USE_RAG

OLLAMA_API_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3.2:3b"
def call_ollama(prompt):
    """Call Ollama API to analyze text"""
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
            timeout=300
        )

        if response.status_code == 200:
            result = response.json()
            return result.get('response', '').strip()
        else:
            print(f"❌ Ollama API error: {response.status_code}")
            print(f"   Make sure Ollama is running: 'ollama serve'")
            print(f"   And model is installed: 'ollama pull {MODEL_NAME}'")
            return None

    except requests.exceptions.ConnectionError:
        print(f"❌ Cannot connect to Ollama at {OLLAMA_API_URL}")
        print(f"   Start Ollama with: 'ollama serve'")
        return None
    except requests.exceptions.Timeout:
        print("❌ Ollama API timeout (model taking too long)")
        return None
    except Exception as e:
        print(f"❌ Error calling Ollama: {e}")
        return None

def extract_job_info(email_data, rag_engine=None):
    """Extract job application info using AI (with RAG support)

    Args:
        email_data: Dictionary with email details
        rag_engine: Pre-initialized RAG engine (optional, for performance)
    """

    subject = email_data.get('subject', '')
    sender = email_data.get('from', '')
    body = email_data.get('body', '')[:2000]

    # ===== NEW: RAG ENHANCEMENT =====
    rag_context = ""
    similar_apps = []

    if USE_RAG and rag_engine is not None:
        try:
            # Search for similar past applications
            search_query = f"{subject}\n\n{body[:500]}"
            similar_apps = rag_engine.search_similar_applications(
                query_text=search_query,
                top_k=3
            )

            if similar_apps:
                # Build context for the prompt
                rag_context = "\n=== CONTEXT: SIMILAR PAST APPLICATIONS ===\n"
                for i, app in enumerate(similar_apps, 1):
                    meta = app['metadata']
                    rag_context += f"{i}. {meta['company']} - {meta['position']} (Status: {meta['status']}, Similarity: {app['similarity']*100:.0f}%)\n"

                rag_context += "\nUse this context to improve extraction accuracy.\n"
                print(f"  ✓ RAG: Found {len(similar_apps)} similar applications")
            else:
                print(f"  ℹ️ RAG: No similar applications found (might be a new company/role)")

        except Exception as e:
            print(f"  ⚠️ RAG search failed (continuing without context): {e}")
            import traceback
            traceback.print_exc()
            rag_context = ""
    elif USE_RAG and rag_engine is None:
        print(f"  ℹ️ RAG engine not available (was initialization successful?)")
    # ===== END RAG ENHANCEMENT =====
    
    # Build prompt with optional RAG context
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
        response = re.sub(r'```json\n?|\n?```', '', response)
        response = response.strip()
        
        json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', response, re.DOTALL)
        if json_match:
            response = json_match.group()
        
        data = json.loads(response)
        
        if not all(key in data for key in ['company', 'role', 'status', 'is_job_related']):
            print(f"Missing fields in: {response[:100]}")
            return None
        
        # Add email metadata
        data['email_subject'] = subject
        data['email_from'] = sender
        data['email_date'] = email_data.get('date', '')
        data['email_body'] = body  # Need this for RAG indexing later
        
        # ===== NEW: Add RAG metadata =====
        data['rag_used'] = USE_RAG and len(similar_apps) > 0
        data['similar_count'] = len(similar_apps)
        # ===== END NEW =====
        
        return data
        
    except json.JSONDecodeError as e:
        print(f"JSON parse error: {response[:150]}")
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None

def analyze_with_ollama(email_subject: str, 
                        email_body: str,
                        app_id: Optional[str] = None) -> Dict:
    """
    Analyze email with optional RAG context
    
    Args:
        email_subject: Email subject line
        email_body: Email body text
        app_id: Optional application ID (to exclude from RAG search)
        
    Returns:
        Dictionary with analysis results
    """
    
    # === RAG ENHANCEMENT ===
    rag_context = ""
    similar_apps = []

    if USE_RAG:
        try:
            # Lazy import to avoid module-level initialization issues
            from rag_engine import get_rag_engine

            # 1. Get RAG engine
            rag_engine = get_rag_engine()

            # 2. Create search query from email
            search_query = f"{email_subject}\n\n{email_body[:500]}"

            # 3. Find similar past applications
            similar_apps = rag_engine.search_similar_applications(
                query_text=search_query,
                exclude_id=app_id,
                top_k=3
            )

            # 4. Build context string for prompt
            if similar_apps:
                rag_context = rag_engine.build_rag_context(similar_apps)
                print(f"✓ RAG: Found {len(similar_apps)} similar applications")
            else:
                print("✓ RAG: No similar applications found (this might be a new company/role)")

        except Exception as e:
            print(f"⚠ RAG error (continuing without context): {e}")
            import traceback
            traceback.print_exc()
            rag_context = ""
    
    # === BUILD ENHANCED PROMPT ===
    prompt = f"""
You are an expert job application analyzer.

{rag_context}

=== NEW EMAIL TO ANALYZE ===
Subject: {email_subject}

Body:
{email_body}

===TASK===
Based on the email above{' and similar past applications' if rag_context else ''}, provide:

1. **Status**: Categorize as one of: Applied, Interview, Offer, Rejection, Follow-up
2. **Company**: Extract company name
3. **Position**: Extract job title/position
4. **Key Information**: 
   - Interview date/time (if mentioned)
   - Salary/compensation (if mentioned)
   - Next steps or deadlines
5. **Recommended Actions**: What should the user do next?
6. **Similarity Insights**: {f'This email is similar to {len(similar_apps)} past application(s). Consider patterns from those experiences.' if similar_apps else 'This appears to be a new type of application.'}

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
    
    # === CALL OLLAMA LLM ===
    try:
        response = requests.post(
            OLLAMA_API_URL,
            json={
                "model": MODEL_NAME,
                "prompt": prompt,
                "stream": False,
                "temperature": 0.3  # Lower = more consistent
            },
            timeout=120
        )
        
        if response.status_code == 200:
            result = response.json()
            analysis_text = result.get('response', '')
            
            # Try to parse JSON response
            try:
                # Extract JSON from response (handle markdown code blocks)
                if '```json' in analysis_text:
                    json_start = analysis_text.find('```json') + 7
                    json_end = analysis_text.find('```', json_start)
                    analysis_text = analysis_text[json_start:json_end]
                
                analysis = json.loads(analysis_text.strip())
                
                # Add RAG metadata
                analysis['rag_used'] = USE_RAG and len(similar_apps) > 0
                analysis['similar_count'] = len(similar_apps)
                
                return analysis
                
            except json.JSONDecodeError:
                # Fallback: return unstructured text
                return {
                    "status": "Unknown",
                    "company": "Unknown",
                    "position": "Unknown",
                    "raw_analysis": analysis_text,
                    "rag_used": USE_RAG and len(similar_apps) > 0,
                    "similar_count": len(similar_apps)
                }
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

if __name__ == "__main__":
    print("=" * 70)
    print("AI ANALYZER TEST - MISTRAL 7B (API)")
    print("=" * 70)
    
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get('models', [])
            model_names = [m['name'] for m in models]
            print(f"\n✓ Ollama running. Models: {', '.join(model_names)}")
            
            if 'mistral:7b' not in model_names:
                print("\n⚠️  Warning: mistral:7b not found!")
                print("Run: ollama pull mistral:7b")
        else:
            print("\n❌ Ollama not responding")
            exit(1)
    except:
        print("\n❌ Ollama not running!")
        exit(1)
    
    print("\n" + "=" * 70)
    
    test_emails = [
        {
            'subject': 'Thank you for applying to Software Engineer at Google',
            'from': 'Google Careers <noreply@google.com>',
            'body': 'Dear Candidate, Thank you for your interest in the Software Engineer position at Google. We have received your application and our team will review it.',
            'date': '2025-10-20'
        },
        {
            'subject': 'Interview Invitation - Product Manager Role',
            'from': 'Microsoft Recruiting <recruiting@microsoft.com>',
            'body': 'Hi, We would like to schedule an interview for the Product Manager position. Are you available next week?',
            'date': '2025-10-21'
        },
        {
            'subject': '50% OFF Everything - Limited Time!',
            'from': 'Promotions <deals@shopping.com>',
            'body': 'Huge sale! Get 50% off all items. Shop now!',
            'date': '2025-10-22'
        }
    ]
    
    print("\nTesting with 3 sample emails...\n")
    
    for i, test_email in enumerate(test_emails, 1):
        print(f"--- Test {i} ---")
        print(f"Subject: {test_email['subject']}")
        
        result = extract_job_info(test_email)
        
        if result:
            print(f"✓ Company: {result['company']}")
            print(f"✓ Role: {result['role']}")
            print(f"✓ Status: {result['status']}")
            print(f"✓ Job Related: {result['is_job_related']}\n")
        else:
            print(f"❌ Failed\n")