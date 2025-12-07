import os
from datetime import datetime
import threading

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import logging

import database
from email_fetcher import fetch_job_emails
from rag_engine import get_rag_engine
from agents import EmailResponseAgent, CompanyResearchAgent, InterviewPrepAgent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize agents (will be set up after app creation)
email_agent = None
research_agent = None
interview_agent = None
scan_status_lock = threading.Lock()
app = Flask(__name__, static_folder='frontend')
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Initialize database
database.init_database()

# Initialize agents after app creation
def init_agents():
    """Initialize AI agents"""
    global email_agent, research_agent, interview_agent
    try:
        logger.info("Initializing AI agents...")
        email_agent = EmailResponseAgent()
        research_agent = CompanyResearchAgent()
        # Don't initialize RAG here - do it per-request to avoid conflicts
        interview_agent = InterviewPrepAgent()
        logger.info("✓ All agents initialized successfully")
    except Exception as e:
        logger.error(f"❌ Failed to initialize agents: {e}")
        raise

init_agents()

# Track scan status (protected by scan_status_lock)
scan_status = {
    'running': False,
    'progress': 0,
    'message': '',
    'total_emails': 0,
    'processed': 0
}

def update_scan_status(**kwargs):
    """Thread-safe scan status update"""
    with scan_status_lock:
        scan_status.update(kwargs)

def run_scan_job(days_back):
    """Background job to scan emails"""
    try:
        print("\n" + "="*70)
        print("SCAN JOB STARTED")
        print("="*70)

        update_scan_status(running=True, message='Starting scan...', progress=5)

        # Check if Ollama is running before starting
        try:
            import requests
            response = requests.get("http://localhost:11434/api/tags", timeout=5)
            if response.status_code != 200:
                raise Exception("Ollama is not responding")
            print("✓ Ollama is running")
        except Exception as e:
            update_scan_status(
                message='Error: Ollama is not running. Please start it with: ollama serve',
                running=False,
                progress=0
            )
            print(f"❌ Ollama check failed: {e}")
            print("   Start Ollama with: ollama serve")
            return

        update_scan_status(message='Fetching emails from Gmail...', progress=10)

        # Fetch emails
        print("→ Fetching emails...")
        emails = fetch_job_emails(days_back=days_back)
        print(f"✓ Fetched {len(emails)} emails")

        update_scan_status(total_emails=len(emails), progress=30)

        if not emails:
            update_scan_status(message='No emails found', running=False)
            print("✓ Scan completed - no emails found")
            return

        # ===== Initialize RAG engine if enabled (BEFORE analyzing emails) =====
        from config import USE_RAG
        rag_engine_instance = None
        if USE_RAG:
            try:
                update_scan_status(
                    message='Initializing RAG engine (may take 1-2 min on first run)...',
                    progress=35
                )
                print("→ Initializing RAG engine (downloading model if needed)...")

                rag_engine_instance = get_rag_engine()

                update_scan_status(progress=38)
                print("✓ RAG engine initialized")
            except Exception as e:
                print(f"⚠️ RAG initialization failed: {e}")
                import traceback
                traceback.print_exc()
                update_scan_status(
                    message=f'RAG initialization failed - continuing without RAG: {str(e)}'
                )
                rag_engine_instance = None
        # ===== END RAG INITIALIZATION =====

        update_scan_status(
            message=f'Analyzing {len(emails)} emails with AI...',
            progress=40
        )
        print(f"→ Starting AI analysis of {len(emails)} emails...")

        # Import AI analyzer (do this once, not in loop)
        print("→ Importing AI analyzer...")
        try:
            from ai_analyzer import extract_job_info
            print("✓ AI analyzer imported successfully")
        except Exception as e:
            print(f"❌ Failed to import AI analyzer: {e}")
            import traceback
            traceback.print_exc()
            scan_status['message'] = f'Error: Failed to load AI analyzer - {str(e)}'
            scan_status['running'] = False
            scan_status['progress'] = 0
            return

        # Analyze emails
        job_applications = []
        for i, email in enumerate(emails):
            print(f"→ Analyzing email {i+1}/{len(emails)}: {email.get('subject', 'No subject')[:50]}...")

            update_scan_status(
                processed=i + 1,
                progress=40 + int((i / len(emails)) * 50),
                message=f'Analyzing email {i+1}/{len(emails)} with AI (may take 1-2 min per email)...'
            )

            try:
                # Pass rag_engine to avoid re-initialization
                job_info = extract_job_info(email, rag_engine=rag_engine_instance)

                if job_info and job_info.get('is_job_related'):
                    job_applications.append(job_info)
                    print(f"  ✓ Found job: {job_info.get('company')} - {job_info.get('role')}")
                else:
                    print(f"  ℹ️ Not job-related")
            except Exception as e:
                print(f"  ⚠️ Error analyzing email: {e}")
                import traceback
                traceback.print_exc()

        update_scan_status(message='Saving to database...', progress=90)
        print(f"→ Saving {len(job_applications)} jobs to database...")

        # Save to database AND index in RAG
        added = 0
        for job in job_applications:
            # Save to SQLite database and get the inserted ID
            job_id = database.add_job_to_db(job)

            if job_id:
                added += 1

                # ===== NEW: Index in RAG vector database =====
                if USE_RAG and rag_engine_instance:
                    try:
                        # Index in vector database
                        rag_engine_instance.add_application(
                            app_id=str(job_id),
                            company=job.get('company', 'Unknown'),
                            position=job.get('role', 'Unknown'),
                            email_subject=job.get('email_subject', ''),
                            email_body=job.get('email_body', ''),
                            status=job.get('status', 'Applied'),
                            notes=job.get('notes', '')
                        )

                        print(f"  ✓ RAG indexed: {job.get('company')} - {job.get('role')}")

                    except Exception as rag_error:
                        # Don't crash if RAG fails - it's optional
                        print(f"  ⚠️ RAG indexing failed for job {job.get('company')}: {rag_error}")
                # ===== END NEW =====

        # Record scan history
        print("→ Recording scan history...")
        database.add_scan_history(days_back, len(emails), len(job_applications))

        # ===== NEW: Update status message to show RAG usage =====
        rag_status = " (with RAG indexing)" if USE_RAG and rag_engine_instance else ""
        update_scan_status(
            message=f'Complete! Found {len(job_applications)} jobs, added {added} new{rag_status}',
            progress=100,
            running=False
        )
        # ===== END NEW =====

        print("="*70)
        print("SCAN JOB COMPLETED SUCCESSFULLY")
        print(f"Found: {len(job_applications)} jobs, Added: {added} new")
        print("="*70 + "\n")

    except Exception as e:
        print("="*70)
        print("SCAN JOB FAILED")
        print(f"Error: {e}")
        print("="*70)
        import traceback
        traceback.print_exc()

        update_scan_status(
            message=f'Error: {str(e)}',
            running=False,
            progress=0
        )

@app.route('/')
def index():
    """Serve frontend"""
    return send_from_directory('frontend', 'index.html')

@app.route('/api/jobs', methods=['GET'])
def get_jobs():
    """Get all job applications"""
    jobs = database.get_all_jobs()
    return jsonify(jobs)

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get statistics"""
    stats = database.get_stats()
    return jsonify(stats)

@app.route('/api/scan', methods=['POST'])
def start_scan():
    """Start email scan"""
    with scan_status_lock:
        if scan_status['running']:
            return jsonify({'error': 'Scan already running'}), 400

    data = request.json or {}
    days_back = data.get('days_back', 60)

    # Validate input
    try:
        days_back = int(days_back)
        if days_back < 1 or days_back > 365:
            return jsonify({'error': 'days_back must be between 1 and 365'}), 400
    except (ValueError, TypeError):
        return jsonify({'error': 'Invalid days_back value'}), 400

    # Start scan in background thread
    thread = threading.Thread(target=run_scan_job, args=(days_back,), daemon=True)
    thread.start()

    with scan_status_lock:
        return jsonify({'message': 'Scan started', 'status': dict(scan_status)})

@app.route('/api/scan/status', methods=['GET'])
def get_scan_status():
    """Get current scan status"""
    with scan_status_lock:
        return jsonify(dict(scan_status))

@app.route('/api/job/<int:job_id>', methods=['PUT'])
def update_job(job_id):
    """Update job status/notes"""
    data = request.json
    status = data.get('status')
    notes = data.get('notes', '')
    
    database.update_job_status(job_id, status, notes)
    return jsonify({'message': 'Updated successfully'})

@app.route('/api/agents/email/analyze', methods=['POST'])
def analyze_email():
    """Analyze incoming email and suggest actions"""
    try:
        data = request.json
        email_data = {
            'from': data.get('from'),
            'subject': data.get('subject'),
            'body': data.get('body'),
            'received_date': data.get('received_date')
        }
        
        logger.info(f"Analyzing email: {email_data.get('subject')}")
        
        # Run email agent in analyze mode
        result = email_agent.run_email_workflow(email_data, action="analyze")
        
        return jsonify({
            'success': True,
            'analysis': result
        })
        
    except Exception as e:
        logger.error(f"Email analysis failed: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/agents/email/draft', methods=['POST'])
def draft_email_response():
    """Draft email response using agent"""
    try:
        data = request.json
        email_data = {
            'from': data.get('from'),
            'subject': data.get('subject'),
            'body': data.get('body'),
            'received_date': data.get('received_date')
        }
        
        logger.info(f"Drafting response to: {email_data.get('subject')}")
        
        # Run email agent in draft mode
        result = email_agent.run_email_workflow(email_data, action="draft")
        
        # Extract draft from observations
        draft = None
        for obs in result.get('observations', []):
            if obs.get('tool') == 'email_drafter':
                draft = obs.get('result')
                break
        
        return jsonify({
            'success': True,
            'draft': draft,
            'agent_state': {
                'status': result.get('status'),
                'iterations': result.get('iterations'),
                'tools_used': result.get('tools_used', [])
            }
        })
        
    except Exception as e:
        logger.error(f"Email draft failed: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/agents/email/send', methods=['POST'])
def send_email_with_agent():
    """Send email after user approval"""
    try:
        data = request.json
        
        # Validate approval
        if not data.get('approved'):
            return jsonify({
                'success': False,
                'error': 'Email not approved'
            }), 400
        
        email_data = data.get('email_data')
        draft = data.get('draft')
        
        logger.info(f"Sending approved email to: {email_data.get('from')}")
        
        # Send via agent
        result = email_agent.send_email(
            to=email_data.get('from'),
            subject=f"Re: {email_data.get('subject')}",
            body=draft
        )
        
        return jsonify({
            'success': result.get('success', False),
            'result': result
        })
        
    except Exception as e:
        logger.error(f"Email send failed: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ===== RESEARCH AGENT ROUTES =====

@app.route('/api/agents/research', methods=['POST'])
def research_company():
    """Research company using autonomous agent"""
    try:
        data = request.json
        company = data.get('company')
        position = data.get('position')
        location = data.get('location')
        
        if not company:
            return jsonify({
                'success': False,
                'error': 'Company name required'
            }), 400
        
        logger.info(f"Starting research: {company}")
        
        # Run research agent
        result = research_agent.research(
            company=company,
            position=position,
            location=location
        )
        
        return jsonify({
            'success': True,
            'status': result.get('status'),
            'observations': result.get('observations', []),
            'tools_used': result.get('tools_used', []),
            'iterations': result.get('iterations')
        })
        
    except Exception as e:
        logger.error(f"Company research failed: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/agents/research/approve', methods=['POST'])
def approve_research():
    """Approve research and get final report"""
    try:
        data = request.json
        agent_state = data.get('agent_state')
        
        if not data.get('approved'):
            return jsonify({
                'success': False,
                'error': 'Research not approved'
            }), 400
        
        logger.info("Compiling approved research report")
        
        # Mark as approved and get report
        agent_state['approved'] = True
        result = research_agent.approve_and_execute(agent_state)
        
        return jsonify({
            'success': True,
            'report': result.get('report'),
            'data': result.get('data')
        })
        
    except Exception as e:
        logger.error(f"Research approval failed: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ===== INTERVIEW PREP AGENT ROUTES =====

@app.route('/api/agents/interview-prep', methods=['POST'])
def prepare_interview():
    """Prepare for interview using agent"""
    try:
        data = request.json
        company = data.get('company')
        position = data.get('position')
        interview_date = data.get('interview_date')
        available_hours = data.get('available_hours', 20)
        
        if not all([company, position, interview_date]):
            return jsonify({
                'success': False,
                'error': 'Company, position, and interview date required'
            }), 400
        
        logger.info(f"Starting interview prep: {position} at {company}")
        
        # Run interview prep agent
        result = interview_agent.prepare(
            company=company,
            position=position,
            interview_date=interview_date,
            available_hours=available_hours
        )
        
        return jsonify({
            'success': True,
            'status': result.get('status'),
            'observations': result.get('observations', []),
            'tools_used': result.get('tools_used', []),
            'iterations': result.get('iterations')
        })
        
    except Exception as e:
        logger.error(f"Interview prep failed: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/agents/interview-prep/approve', methods=['POST'])
def approve_interview_prep():
    """Approve prep plan and get final guide"""
    try:
        data = request.json
        agent_state = data.get('agent_state')
        
        if not data.get('approved'):
            return jsonify({
                'success': False,
                'error': 'Prep plan not approved'
            }), 400
        
        logger.info("Compiling approved interview prep guide")
        
        # Mark as approved and get guide
        agent_state['approved'] = True
        result = interview_agent.approve_and_execute(agent_state)
        
        return jsonify({
            'success': True,
            'guide': result.get('guide'),
            'data': result.get('data')
        })
        
    except Exception as e:
        logger.error(f"Interview prep approval failed: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ===== AGENT STATUS & MONITORING =====

@app.route('/api/agents/status', methods=['GET'])
def get_agents_status():
    """Get status of all agents"""
    try:
        return jsonify({
            'success': True,
            'agents': {
                'email_agent': {
                    'available': True,
                    'tools': list(email_agent.tools.keys())
                },
                'research_agent': {
                    'available': True,
                    'tools': list(research_agent.tools.keys())
                },
                'interview_agent': {
                    'available': True,
                    'tools': list(interview_agent.tools.keys()),
                    'rag_enabled': interview_agent.rag_engine is not None
                }
            }
        })
    except Exception as e:
        logger.error(f"Agent status check failed: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
@socketio.on('connect')
def handle_connect():
    logger.info('Client connected to agent updates')
    emit('agent_status', {'status': 'connected'})

@socketio.on('agent_progress')
def handle_agent_progress(data):
    """Emit real-time agent progress updates"""
    emit('agent_update', {
        'agent': data.get('agent'),
        'step': data.get('step'),
        'status': data.get('status'),
        'timestamp': datetime.now().isoformat()
    }, broadcast=True)

if __name__ == '__main__':
    print("=" * 70)
    print("    JOB TRACKER - Starting Web Server")
    print("=" * 70)
    print("\n🌐 Open your browser and go to: http://localhost:5000")
    print("\n✨ Features:")
    print("   - View all job applications")
    print("   - Scan emails anytime with one click")
    print("   - Real-time progress tracking")
    print("   - Update status and add notes")
    print("\n" + "=" * 70 + "\n")

    # Use socketio.run instead of app.run for WebSocket support
    socketio.run(app, debug=True, port=5000, host='0.0.0.0')