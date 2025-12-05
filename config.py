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
# ==================== RAG CONFIGURATION ====================

# Embedding Model (local, no API key needed)
EMBEDDING_MODEL = "all-MiniLM-L6-v2"  # Fast, 384-dim embeddings
# Alternative: "all-mpnet-base-v2"  # Slower but more accurate, 768-dim

# Vector Database
CHROMA_DB_PATH = "./chroma_db"  # Where to store vector database
COLLECTION_NAME = "job_applications"  # ChromaDB collection name

# RAG Settings
TOP_K_RESULTS = 3  # How many similar past applications to retrieve
SIMILARITY_THRESHOLD = 0.7  # Minimum similarity score (0-1)

# What to index for RAG
RAG_FIELDS = [
    "company_name",
    "position", 
    "email_subject",
    "email_body",
    "notes"  # User notes from past applications
]

# Enable/Disable RAG
USE_RAG = True  # Lightweight TF-IDF based RAG