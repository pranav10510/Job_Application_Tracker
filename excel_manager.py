import pandas as pd
from datetime import datetime
import os
import config

def create_or_load_spreadsheet():
    """Create new spreadsheet or load existing one"""
    if os.path.exists(config.OUTPUT_FILE):
        df = pd.read_excel(config.OUTPUT_FILE)
        print(f"✓ Loaded existing spreadsheet: {len(df)} entries")
    else:
        df = pd.DataFrame(columns=[
            'Company',
            'Role',
            'Date Applied',
            'Status',
            'Email Subject',
            'Email From',
            'Notes'
        ])
        print("✓ Created new spreadsheet")
    
    return df

def is_duplicate(df, company, role):
    """Check if this application already exists"""
    if df.empty:
        return False
    
    # Check for similar company and role
    duplicates = df[
        (df['Company'].str.lower() == company.lower()) &
        (df['Role'].str.lower() == role.lower())
    ]
    
    return len(duplicates) > 0

def add_job_application(df, job_info):
    """Add a new job application to the dataframe"""
    
    company = job_info.get('company', 'Unknown')
    role = job_info.get('role', 'Unknown')
    
    # Skip if duplicate
    if is_duplicate(df, company, role):
        return df, False
    
    # Parse date
    email_date = job_info.get('email_date', '')
    try:
        date_applied = pd.to_datetime(email_date).strftime('%Y-%m-%d')
    except:
        date_applied = datetime.now().strftime('%Y-%m-%d')
    
    # Create new row
    new_row = {
        'Company': company,
        'Role': role,
        'Date Applied': date_applied,
        'Status': job_info.get('status', 'Other'),
        'Email Subject': job_info.get('email_subject', '')[:100],
        'Email From': job_info.get('email_from', '')[:50],
        'Notes': ''
    }
    
    # Add to dataframe
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    
    return df, True

def save_spreadsheet(df):
    """Save dataframe to Excel file"""
    df.to_excel(config.OUTPUT_FILE, index=False)
    print(f"\n✓ Saved to {config.OUTPUT_FILE}")

def update_spreadsheet_with_jobs(job_applications):
    """Update spreadsheet with multiple job applications"""
    print("\n📊 Updating spreadsheet...")
    
    df = create_or_load_spreadsheet()
    
    added_count = 0
    duplicate_count = 0
    
    for job in job_applications:
        df, added = add_job_application(df, job)
        if added:
            added_count += 1
            print(f"  ✓ Added: {job['company']} - {job['role']}")
        else:
            duplicate_count += 1
            print(f"  ⊘ Duplicate: {job['company']} - {job['role']}")
    
    # Sort by date
    df['Date Applied'] = pd.to_datetime(df['Date Applied'])
    df = df.sort_values('Date Applied', ascending=False)
    df['Date Applied'] = df['Date Applied'].dt.strftime('%Y-%m-%d')
    
    save_spreadsheet(df)
    
    print(f"\n📈 Summary:")
    print(f"  New applications added: {added_count}")
    print(f"  Duplicates skipped: {duplicate_count}")
    print(f"  Total applications: {len(df)}")
    
    return df

if __name__ == "__main__":
    # Test the Excel manager
    print("=" * 70)
    print("EXCEL MANAGER TEST")
    print("=" * 70)
    
    test_jobs = [
        {
            'company': 'Google',
            'role': 'Software Engineer',
            'status': 'Applied',
            'email_subject': 'Thank you for applying',
            'email_from': 'careers@google.com',
            'email_date': '2025-10-20'
        },
        {
            'company': 'Microsoft',
            'role': 'Product Manager',
            'status': 'Interview',
            'email_subject': 'Interview invitation',
            'email_from': 'recruiting@microsoft.com',
            'email_date': '2025-10-21'
        }
    ]
    
    df = update_spreadsheet_with_jobs(test_jobs)
    
    print("\n📋 Spreadsheet Preview:")
    print(df[['Company', 'Role', 'Date Applied', 'Status']])