import os
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

import pickle
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from datetime import datetime, timedelta
import base64
from email import message_from_bytes
import re
import config

def get_gmail_service():
    """Get authenticated Gmail service"""
    creds = None
    
    if os.path.exists(config.TOKEN_FILE):
        with open(config.TOKEN_FILE, 'rb') as token:
            creds = pickle.load(token)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                config.CREDENTIALS_FILE, config.SCOPES,
                redirect_uri='http://localhost:8080'
            )
            auth_url, _ = flow.authorization_url(
                access_type='offline', prompt='consent'
            )
            print(f"Visit: {auth_url}")
            code = input("Paste redirect URL: ").strip()
            flow.fetch_token(authorization_response=code)
            creds = flow.credentials
        
        with open(config.TOKEN_FILE, 'wb') as token:
            pickle.dump(creds, token)
    
    return build('gmail', 'v1', credentials=creds)

def get_email_body(payload):
    """Extract email body from payload"""
    body = ""
    
    if 'parts' in payload:
        for part in payload['parts']:
            if part['mimeType'] == 'text/plain':
                if 'data' in part['body']:
                    body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                    break
            elif part['mimeType'] == 'text/html' and not body:
                if 'data' in part['body']:
                    body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
    else:
        if 'body' in payload and 'data' in payload['body']:
            body = base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8')
    
    return body

def fetch_job_emails(days_back=60):
    """Fetch job-related emails from Gmail"""
    print(f"\n📧 Fetching job emails from last {days_back} days...")
    
    service = get_gmail_service()
    
    # Calculate date
    date_from = (datetime.now() - timedelta(days=days_back)).strftime('%Y/%m/%d')
    
    # Build search query
    query_parts = [f'after:{date_from}']
    query_parts.append('(' + ' OR '.join(config.JOB_KEYWORDS) + ')')
    query = ' '.join(query_parts)
    
    print(f"Search query: {query}")
    
    # Fetch messages
    results = service.users().messages().list(
        userId='me',
        q=query,
        maxResults=500
    ).execute()
    
    messages = results.get('messages', [])
    print(f"✓ Found {len(messages)} potential job emails")
    
    # Fetch full message details
    emails = []
    for i, msg in enumerate(messages, 1):
        try:
            message = service.users().messages().get(
                userId='me',
                id=msg['id'],
                format='full'
            ).execute()
            
            headers = {h['name']: h['value'] 
                      for h in message['payload']['headers']}
            
            email_data = {
                'id': msg['id'],
                'subject': headers.get('Subject', 'No Subject'),
                'from': headers.get('From', 'Unknown'),
                'date': headers.get('Date', ''),
                'body': get_email_body(message['payload'])
            }
            
            emails.append(email_data)
            
            if i % 10 == 0:
                print(f"  Processed {i}/{len(messages)} emails...")
                
        except Exception as e:
            print(f"  Error processing message {msg['id']}: {e}")
            continue
    
    print(f"✓ Successfully fetched {len(emails)} emails\n")
    return emails

if __name__ == "__main__":
    # Test the fetcher
    print("=" * 70)
    print("EMAIL FETCHER TEST")
    print("=" * 70)
    
    emails = fetch_job_emails(days_back=30)
    
    print("\n📊 Sample emails:")
    for i, email in enumerate(emails[:3], 1):
        print(f"\n{i}. Subject: {email['subject'][:60]}")
        print(f"   From: {email['from'][:50]}")
        print(f"   Date: {email['date']}")
        print(f"   Body preview: {email['body'][:100]}...")