import sqlite3
from datetime import datetime
import os

DB_FILE = "job_tracker.db"

def init_database():
    """Initialize SQLite database"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS job_applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company TEXT NOT NULL,
            role TEXT NOT NULL,
            date_applied TEXT,
            status TEXT,
            email_subject TEXT,
            email_from TEXT,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(company, role)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS scan_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            scan_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            days_back INTEGER,
            emails_scanned INTEGER,
            jobs_found INTEGER
        )
    ''')
    
    conn.commit()
    conn.close()
    print("✓ Database initialized")

def add_job_to_db(job_info):
    """Add job application to database"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            INSERT INTO job_applications 
            (company, role, date_applied, status, email_subject, email_from, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            job_info.get('company', 'Unknown'),
            job_info.get('role', 'Unknown'),
            job_info.get('email_date', datetime.now().strftime('%Y-%m-%d')),
            job_info.get('status', 'Other'),
            job_info.get('email_subject', ''),
            job_info.get('email_from', ''),
            ''
        ))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        # Duplicate entry
        conn.close()
        return False

def get_all_jobs():
    """Get all job applications"""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT * FROM job_applications 
        ORDER BY date_applied DESC
    ''')
    
    jobs = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jobs

def get_stats():
    """Get statistics"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute('SELECT COUNT(*) FROM job_applications')
    total = cursor.fetchone()[0]
    
    cursor.execute('SELECT status, COUNT(*) FROM job_applications GROUP BY status')
    status_counts = dict(cursor.fetchall())
    
    conn.close()
    
    return {
        'total': total,
        'status_counts': status_counts
    }

def add_scan_history(days_back, emails_scanned, jobs_found):
    """Record scan history"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO scan_history (days_back, emails_scanned, jobs_found)
        VALUES (?, ?, ?)
    ''', (days_back, emails_scanned, jobs_found))
    
    conn.commit()
    conn.close()

def update_job_status(job_id, status, notes):
    """Update job status and notes"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute('''
        UPDATE job_applications 
        SET status = ?, notes = ?
        WHERE id = ?
    ''', (status, notes, job_id))
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_database()
    print("Database initialized successfully!")