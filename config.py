# config.py

# Gmail Settings
GMAIL_ADDRESS = "pranavpenjarla@gmail.com"
CREDENTIALS_FILE = "credentials.json"
TOKEN_FILE = "token.pkl"  # Changed to .pkl for pickle

# Gmail API Scopes
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

# Output file settings
OUTPUT_FILE = "job_applications.xlsx"

# Default scan period (in days)
DEFAULT_DAYS_BACK = 60

# Keywords to identify job-related emails
JOB_KEYWORDS = [
    "application", "applied", "position", "role", "job",
    "interview", "assessment", "opportunity", "linkedin",
    "thank you for applying", "application received",
    "noreply", "jobs-noreply", "recruiting"
]