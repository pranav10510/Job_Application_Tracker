import os
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import threading
import database
from email_fetcher import fetch_job_emails

app = Flask(__name__, static_folder='frontend')
CORS(app)

# Initialize database
database.init_database()

# Track scan status
scan_status = {
    'running': False,
    'progress': 0,
    'message': '',
    'total_emails': 0,
    'processed': 0
}

def run_scan_job(days_back):
    """Background job to scan emails"""
    global scan_status

    try:
        print("\n" + "="*70)
        print("SCAN JOB STARTED")
        print("="*70)

        scan_status['running'] = True
        scan_status['message'] = 'Starting scan...'
        scan_status['progress'] = 5

        # Check if Ollama is running before starting
        try:
            import requests
            response = requests.get("http://localhost:11434/api/tags", timeout=5)
            if response.status_code != 200:
                raise Exception("Ollama is not responding")
            print("✓ Ollama is running")
        except Exception as e:
            scan_status['message'] = f'Error: Ollama is not running. Please start it with: ollama serve'
            scan_status['running'] = False
            scan_status['progress'] = 0
            print(f"❌ Ollama check failed: {e}")
            print("   Start Ollama with: ollama serve")
            return

        scan_status['message'] = 'Fetching emails from Gmail...'
        scan_status['progress'] = 10

        # Fetch emails
        print("→ Fetching emails...")
        emails = fetch_job_emails(days_back=days_back)
        print(f"✓ Fetched {len(emails)} emails")

        scan_status['total_emails'] = len(emails)
        scan_status['progress'] = 30

        if not emails:
            scan_status['message'] = 'No emails found'
            scan_status['running'] = False
            print("✓ Scan completed - no emails found")
            return

        # ===== Initialize RAG engine if enabled (BEFORE analyzing emails) =====
        from config import USE_RAG
        rag_engine = None
        if USE_RAG:
            try:
                scan_status['message'] = 'Initializing RAG engine (may take 1-2 min on first run)...'
                scan_status['progress'] = 35
                print("→ Initializing RAG engine (downloading model if needed)...")

                from rag_engine import get_rag_engine
                rag_engine = get_rag_engine()

                scan_status['progress'] = 38
                print("✓ RAG engine initialized")
            except Exception as e:
                print(f"⚠️ RAG initialization failed: {e}")
                import traceback
                traceback.print_exc()
                scan_status['message'] = f'RAG initialization failed - continuing without RAG: {str(e)}'
                rag_engine = None
        # ===== END RAG INITIALIZATION =====

        scan_status['message'] = f'Analyzing {len(emails)} emails with AI...'
        scan_status['progress'] = 40
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

            scan_status['processed'] = i + 1
            scan_status['progress'] = 40 + int((i / len(emails)) * 50)
            scan_status['message'] = f'Analyzing email {i+1}/{len(emails)} with AI (may take 1-2 min per email)...'

            try:
                # Pass rag_engine to avoid re-initialization
                job_info = extract_job_info(email, rag_engine=rag_engine)

                if job_info and job_info.get('is_job_related'):
                    job_applications.append(job_info)
                    print(f"  ✓ Found job: {job_info.get('company')} - {job_info.get('role')}")
                else:
                    print(f"  ℹ️ Not job-related")
            except Exception as e:
                print(f"  ⚠️ Error analyzing email: {e}")
                import traceback
                traceback.print_exc()
        
        scan_status['message'] = 'Saving to database...'
        scan_status['progress'] = 90
        print(f"→ Saving {len(job_applications)} jobs to database...")

        # Save to database AND index in RAG
        added = 0
        for job in job_applications:
            # Save to SQLite database and get the inserted ID
            job_id = database.add_job_to_db(job)

            if job_id:
                added += 1

                # ===== NEW: Index in RAG vector database =====
                if USE_RAG and rag_engine:
                    try:
                        # Index in vector database
                        rag_engine.add_application(
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
        rag_status = " (with RAG indexing)" if USE_RAG and rag_engine else ""
        scan_status['message'] = f'Complete! Found {len(job_applications)} jobs, added {added} new{rag_status}'
        # ===== END NEW =====

        scan_status['progress'] = 100
        scan_status['running'] = False

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

        scan_status['message'] = f'Error: {str(e)}'
        scan_status['running'] = False
        scan_status['progress'] = 0

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
    if scan_status['running']:
        return jsonify({'error': 'Scan already running'}), 400
    
    data = request.json
    days_back = data.get('days_back', 60)
    
    # Start scan in background thread
    thread = threading.Thread(target=run_scan_job, args=(days_back,))
    thread.start()
    
    return jsonify({'message': 'Scan started', 'status': scan_status})

@app.route('/api/scan/status', methods=['GET'])
def get_scan_status():
    """Get current scan status"""
    return jsonify(scan_status)

@app.route('/api/job/<int:job_id>', methods=['PUT'])
def update_job(job_id):
    """Update job status/notes"""
    data = request.json
    status = data.get('status')
    notes = data.get('notes', '')
    
    database.update_job_status(job_id, status, notes)
    return jsonify({'message': 'Updated successfully'})

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
    
    app.run(debug=True, port=5000, host='0.0.0.0')