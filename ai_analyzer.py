import requests
import json
import re

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
            print(f"Ollama API error: {response.status_code}")
            return None
            
    except requests.exceptions.Timeout:
        print("Ollama API timeout")
        return None
    except Exception as e:
        print(f"Error calling Ollama: {e}")
        return None

def extract_job_info(email_data):
    """Extract job application info using AI"""
    
    subject = email_data.get('subject', '')
    sender = email_data.get('from', '')
    body = email_data.get('body', '')[:2000]
    
    prompt = f"""Extract job info from this email as JSON only:

Subject: {subject}
From: {sender}
Body: {body}

Return this exact format:
{{"company": "name", "role": "title", "status": "Applied|Interview|Assessment|Rejected|Offer|Other", "is_job_related": true}}

Rules:
- company: extract from sender or body
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
        
        data['email_subject'] = subject
        data['email_from'] = sender
        data['email_date'] = email_data.get('date', '')
        
        return data
        
    except json.JSONDecodeError as e:
        print(f"JSON parse error: {response[:150]}")
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None

def analyze_emails(emails):
    """Analyze multiple emails and extract job info"""
    print(f"\n🤖 Analyzing {len(emails)} emails with Mistral 7B AI...")
    
    results = []
    skipped = 0
    
    for i, email in enumerate(emails, 1):
        print(f"  [{i}/{len(emails)}] {email['subject'][:50]}...", end=" ")
        
        job_info = extract_job_info(email)
        
        if job_info:
            if job_info.get('is_job_related'):
                results.append(job_info)
                print(f"✓ {job_info['company']} - {job_info['status']}")
            else:
                skipped += 1
                print(f"⊘ Spam")
        else:
            print(f"⚠ Failed")
    
    print(f"\n✓ Found {len(results)} job applications")
    print(f"⊘ Skipped {skipped} spam emails\n")
    return results

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