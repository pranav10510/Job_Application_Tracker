# config.py
import os

# Gmail Settings (use environment variables for security)
GMAIL_ADDRESS = os.getenv('GMAIL_ADDRESS', '')  # Set via environment variable
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

# LangChain Integration (Phase 2)
USE_LANGCHAIN = True  # Use LangChain chains instead of direct API calls
LANGCHAIN_MODE = "standard"  # Options: "standard", "few_shot", "cot"

# ===== AGENT CONFIGURATION =====

# Enable/disable agents
AGENTS_ENABLED = True
EMAIL_AGENT_ENABLED = True
RESEARCH_AGENT_ENABLED = True
INTERVIEW_AGENT_ENABLED = True

# Agent behavior settings
AGENT_MAX_ITERATIONS = 10  # Maximum planning/action cycles
AGENT_TEMPERATURE = 0.7  # LLM temperature for agents
AGENT_TIMEOUT = 300  # Timeout in seconds (5 minutes)

# Approval settings
REQUIRE_APPROVAL = True  # If False, agents execute autonomously
AUTO_APPROVE_LOW_RISK = False  # Auto-approve low-risk actions (e.g., drafts)

# Email Agent Configuration
EMAIL_AGENT_MODEL = "llama3.2:3b"  # Full model name with tag
EMAIL_TEMPLATES_DIR = "templates/emails"
GMAIL_API_ENABLED = False  # Set to True when Gmail API is configured
GMAIL_CREDENTIALS_FILE = "credentials/gmail_token.json"

# LLM Configuration (centralized)
OLLAMA_MODEL = "llama3.2:3b"  # Full model name with tag
OLLAMA_MODEL_FULL = "llama3.2:3b"  # Full model name with tag
OLLAMA_BASE_URL = "http://localhost:11434"
OLLAMA_TIMEOUT = 300  # seconds

# Research Agent Configuration
RESEARCH_AGENT_MODEL = "llama3.2:3b"
WEB_SEARCH_ENABLED = True
WEB_SEARCH_API_KEY = os.getenv('WEB_SEARCH_API_KEY')  # Set via environment variable
SCRAPING_ENABLED = True
SCRAPING_DELAY = 1  # Delay between requests (seconds)
SCRAPING_USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"

# Interview Prep Agent Configuration
INTERVIEW_AGENT_MODEL = "llama3.2:3b"
RAG_INTEGRATION = True  # Use RAG for past applications
PRACTICE_PROBLEMS_SOURCE = "leetcode"  # Options: leetcode, hackerrank, both
STUDY_PLAN_DEFAULT_HOURS = 20

# Agent monitoring
AGENT_LOGGING_ENABLED = True
AGENT_LOG_FILE = "logs/agents.log"
AGENT_METRICS_ENABLED = True  # Track success rates, execution times

# Rate limiting
AGENT_RATE_LIMIT = 10  # Max agent runs per hour per user
TOOL_RATE_LIMIT = 50  # Max tool calls per hour

# Cache settings
AGENT_CACHE_ENABLED = True
AGENT_CACHE_TTL = 3600  # Cache results for 1 hour

# Tool configurations
TOOLS_CONFIG = {
    'email_drafter': {
        'enabled': True,
        'model': EMAIL_AGENT_MODEL,
        'max_length': 500,  # Max words in draft
    },
    'web_search': {
        'enabled': WEB_SEARCH_ENABLED,
        'api_key': WEB_SEARCH_API_KEY,
        'max_results': 10,
    },
    'website_scraper': {
        'enabled': SCRAPING_ENABLED,
        'timeout': 10,
        'max_pages': 5,
    },
    'salary_lookup': {
        'enabled': True,
        'sources': ['glassdoor', 'levels.fyi', 'ai_estimation'],
    },
    'rag_search': {
        'enabled': RAG_INTEGRATION,
        'k': 5,  # Number of similar applications to retrieve
    },
    'question_generator': {
        'enabled': True,
        'num_questions': 15,
    }
}

# Agent workflow presets
AGENT_WORKFLOWS = {
    'quick_draft': {
        'agent': 'email',
        'mode': 'fast',
        'iterations': 3,
        'auto_approve': False
    },
    'deep_research': {
        'agent': 'research',
        'mode': 'comprehensive',
        'iterations': 10,
        'auto_approve': False
    },
    'rapid_prep': {
        'agent': 'interview',
        'mode': 'focused',
        'hours': 10,
        'auto_approve': False
    }
}

# Notification settings
AGENT_NOTIFICATIONS = {
    'on_completion': True,
    'on_error': True,
    'on_approval_needed': True,
    'email': True,  # Send email notifications
    'in_app': True,  # Show in-app notifications
}