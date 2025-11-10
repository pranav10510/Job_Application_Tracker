import os
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import threading
import database
from email_fetcher import fetch_job_emails
from ai_analyzer import analyze_emails

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
        scan_status['running'] = True
        scan_status['message'] = 'Fetching emails from Gmail...'
        scan_status['progress'] = 10
        
        # Fetch emails
        emails = fetch_job_emails(days_back=days_back)
        scan_status['total_emails'] = len(emails)
        scan_status['progress'] = 30
        
        if not emails:
            scan_status['message'] = 'No emails found'
            scan_status['running'] = False
            return
        
        scan_status['message'] = f'Analyzing {len(emails)} emails with AI...'
        scan_status['progress'] = 40
        
        # Analyze emails
        job_applications = []
        for i, email in enumerate(emails):
            scan_status['processed'] = i + 1
            scan_status['progress'] = 40 + int((i / len(emails)) * 50)
            scan_status['message'] = f'Analyzing email {i+1}/{len(emails)} with AI (may take 1-2 min per email)...'
            
            from ai_analyzer import extract_job_info
            job_info = extract_job_info(email)
            
            if job_info and job_info.get('is_job_related'):
                job_applications.append(job_info)
        
        scan_status['message'] = 'Saving to database...'
        scan_status['progress'] = 90
        
        # Save to database
        added = 0
        for job in job_applications:
            if database.add_job_to_db(job):
                added += 1
        
        # Record scan history
        database.add_scan_history(days_back, len(emails), len(job_applications))
        
        scan_status['message'] = f'Complete! Found {len(job_applications)} jobs, added {added} new'
        scan_status['progress'] = 100
        scan_status['running'] = False
        
    except Exception as e:
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