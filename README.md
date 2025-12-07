# Job Tracker - AI-Powered Job Application Manager

A smart job application tracker that automatically scans your Gmail for job-related emails and organizes them using AI analysis. Features autonomous AI agents for drafting emails, researching companies, and preparing for interviews. Built with Flask, React, Gmail API, and Ollama AI.

## 🌟 Key Features

### 📧 Automatic Email Scanning
- Scans Gmail for job applications, confirmations, and responses
- Smart keyword-based filtering
- Configurable date ranges

### 🤖 Autonomous AI Agents (NEW!)
Three powerful AI agents to automate your job search:

- **📧 Email Agent**: Drafts professional email responses with tone matching and template selection
- **🔍 Research Agent**: Deep company research including news, culture insights, and salary data
- **📚 Interview Agent**: Creates personalized interview prep plans with practice questions

### 🎨 Modern Beautiful UI
- Stunning gradient cards for each agent (purple, pink, cyan)
- Smooth animations and hover effects
- Real-time progress tracking with step-by-step visualization
- Dynamic card expansion
- Professional, responsive design

### 🧠 RAG (Retrieval-Augmented Generation)
- Smart context-aware analysis using past applications
- TF-IDF vectorization for fast similarity search
- Improves AI accuracy over time

### 🔗 LangChain Integration
- Professional AI framework with retry logic
- Autonomous agent state machines using LangGraph
- Tool-based architecture for extensibility

### 📊 Real-time Dashboard
- Live progress tracking during scans
- Filter by status (Applied, Interview, Offer, etc.)
- Modern React UI with dark mode support
- SQLite database for persistent storage

## 🤖 AI Agents - Detailed

### Email Response Agent
**What it does:**
- Analyzes incoming email tone and context
- Selects appropriate response template (interview acceptance, follow-up, thank you, etc.)
- Drafts professional responses matching the sender's tone
- Requires approval before sending

**Features:**
- 5 pre-built templates (interview acceptance/decline, follow-up, thank you, status inquiry)
- AI-generated responses for custom situations
- Tone analysis (formal/casual, urgent/relaxed)
- Gmail integration ready

### Company Research Agent
**What it does:**
- Searches web for company information
- Scrapes company websites
- Finds recent news and developments
- Analyzes company culture from reviews
- Looks up salary data for positions
- Compiles comprehensive research report

**Features:**
- Web search integration
- Website scraping with BeautifulSoup
- News aggregation
- Culture insights from Glassdoor
- Salary estimation
- Professional PDF-ready reports

### Interview Prep Agent
**What it does:**
- Analyzes job requirements from application
- Generates role-specific practice questions
- Creates personalized study plan
- Provides interview tips and strategies
- Uses RAG to learn from your past applications

**Features:**
- Practice question database
- Customized study schedules (based on available hours)
- Technical and behavioral question prep
- Company-specific insights
- Weakness analysis and improvement tips

## 🎬 Agent Demo

### Beautiful Agent Cards
```
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│ Purple Glow  │  │  Pink Glow   │  │  Cyan Glow   │
│     📧       │  │      🔍      │  │      📚      │
│ (floating)   │  │  (floating)  │  │  (floating)  │
│              │  │              │  │              │
│ Email Agent  │  │   Research   │  │  Interview   │
│              │  │    Agent     │  │    Agent     │
│ [LAUNCH] →   │  │  [LAUNCH] →  │  │  [LAUNCH] →  │
└──────────────┘  └──────────────┘  └──────────────┘
```

### Dynamic Progress
```
┌─────────────────────────────────────────┐
│  📧 Email Agent              ×          │
│                                         │
│  ⟳ Working...                           │
│  ────────────────────────────           │
│  ✓ Analyzing tone and context           │
│  ✓ Selecting template                   │
│  ⟳ Drafting response... (active)        │
│  3 Reviewing and formatting             │
│  ────────────────────────────           │
│  Progress: 75% ████████████████░░░░     │
│                                         │
│  ✨ Results Ready                        │
│  Draft: Dear Hiring Manager...          │
│                                         │
│  [✓ Approve & Execute]  [Close]         │
└─────────────────────────────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Node.js 16+ (for React frontend)
- Gmail account with API access
- Ollama installed locally

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd Job_Tracker
```

### 2. Set Up Python Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Linux/Mac:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Set Up Gmail API

#### Step 1: Enable Gmail API
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable the Gmail API:
   - Go to "APIs & Services" → "Library"
   - Search for "Gmail API"
   - Click "Enable"

#### Step 2: Create OAuth Credentials
1. Go to "APIs & Services" → "Credentials"
2. Click "Create Credentials" → "OAuth client ID"
3. Choose "Desktop Application"
4. Download the credentials JSON file
5. **Rename it to `credentials.json`** and place it in the project root

### 4. Set Up Ollama AI

#### Install Ollama
```bash
# On Linux/Mac:
curl -fsSL https://ollama.ai/install.sh | sh

# On Windows: Download from https://ollama.ai/download
```

#### Install the AI Model
```bash
# Install the lightweight model (recommended for agents)
ollama pull llama3.2:3b

# Or install Mistral (larger, slower)
ollama pull mistral:7b
```

#### Start Ollama Service
```bash
ollama serve
```

### 5. First-Time Gmail Authentication

**IMPORTANT**: You must authenticate Gmail via command line first:

```bash
# Run the email fetcher directly
python email_fetcher.py
```

This will:
1. Show you a Google authorization URL
2. Open the URL in your browser
3. Click "Allow" to authorize the app
4. Copy the redirect URL from browser (even if it shows "This site can't be reached")
5. Paste the full URL when prompted

The authentication token will be saved as `token.pkl` for future use.

### 6. Set Up React Frontend

```bash
# Navigate to the React frontend directory
cd job-tracker

# Install Node.js dependencies
npm install

# Start the development server
npm run dev
```

The React frontend will run on **http://localhost:5173**

### 7. Start the Flask Backend

```bash
# From the main project directory
python app.py
```

The Flask API will run on **http://localhost:5000**

### 8. Access the Application

Open your browser and go to **http://localhost:5173**

## 📱 Usage

### Basic Workflow

1. **Dashboard**: View all job applications and statistics
2. **Scan Emails**: Click "Launch Scan" to import new applications
3. **AI Agents**: Select a job and use AI agents to automate tasks

### Using AI Agents

1. **Navigate to AI Agents** (🤖 in sidebar)
2. **Select a Job Application** from the grid
3. **Choose an Agent**:
   - Click "Launch Agent" on Email, Research, or Interview card
4. **Watch Progress**: Real-time steps with animations
5. **Review Results**: See the agent's output
6. **Approve & Execute**: Click to execute the action

### Email Scanning

1. Click "Launch Scan" on Dashboard
2. Choose time range (5 days to 120 days)
3. Monitor real-time progress
4. Review imported applications

## 🔧 Configuration

### Agent Settings

Edit `config.py` to customize agent behavior:

```python
# Agent Configuration
AGENTS_ENABLED = True
EMAIL_AGENT_ENABLED = True
RESEARCH_AGENT_ENABLED = True
INTERVIEW_AGENT_ENABLED = True

# Agent Behavior
AGENT_MAX_ITERATIONS = 10  # Maximum planning cycles
AGENT_TEMPERATURE = 0.7    # LLM creativity (0-1)
REQUIRE_APPROVAL = True    # If False, agents run autonomously
```

### RAG Configuration

```python
# RAG Settings
USE_RAG = True                  # Enable/disable RAG
TOP_K_RESULTS = 3              # Similar apps to retrieve
SIMILARITY_THRESHOLD = 0.7     # Minimum similarity (0-1)
```

### Email Keywords

```python
JOB_KEYWORDS = [
    "application", "applied", "position", "role", "job",
    "interview", "assessment", "opportunity", "linkedin",
    "thank you for applying", "application received",
    "noreply", "jobs-noreply", "recruiting"
]
```

### AI Model Selection

In `config.py`:

```python
OLLAMA_MODEL = "llama3.2:3b"  # Fast, lightweight
# OLLAMA_MODEL = "mistral:7b"  # Slower but more accurate
```

## 🛠 Troubleshooting

### Common Issues

#### "Token has been expired or revoked"
```bash
# Remove expired token and re-authenticate
rm token.pkl
python email_fetcher.py
```

#### "Ollama not running"
```bash
# Start Ollama service
ollama serve

# Check if model is installed
ollama list

# If model missing, install it
ollama pull llama3.2:3b
```

#### Agent Stuck in Loop
- Backend has been updated with termination logic
- Agents now complete in 3-4 iterations
- Check backend logs for "moving to approval"

#### Cards Not Expanding
- Hard refresh browser (Ctrl+Shift+R)
- Clear browser cache
- Ensure you selected a job first

#### Approve Button Not Working
- Check backend is running
- Verify API endpoint in browser console
- Check backend logs for errors

### Performance Tips

- **Use llama3.2:3b** for faster agent responses
- **Scan shorter periods** first (5-30 days)
- **Run agents one at a time** for best results
- **Ensure Ollama has sufficient RAM** (8GB+ recommended)

## 🗂 Project Structure

```
Job_Tracker/
├── app.py                  # Flask backend API
├── email_fetcher.py        # Gmail API integration
├── ai_analyzer.py          # Ollama AI analysis
├── rag_engine.py          # RAG vector search
├── database.py            # SQLite operations
├── config.py              # All configuration
├── agents/                # AI Agent implementations
│   ├── __init__.py
│   ├── base_agent.py      # LangGraph base class
│   ├── email_agent.py     # Email drafting
│   ├── research_agent.py  # Company research
│   ├── interview_agent.py # Interview prep
│   └── tools.py           # Agent tools
├── chains.py              # LangChain chains
├── prompts.py             # Centralized prompts
├── credentials.json       # Gmail API credentials (you create)
├── token.pkl             # Gmail auth token (auto-generated)
├── requirements.txt      # Python dependencies
├── job_tracker.db        # SQLite database (auto-generated)
├── chroma_db/            # RAG vector storage
│   └── tfidf_rag.pkl    # TF-IDF index
└── job-tracker/          # Modern React frontend
    ├── src/
    │   ├── App.jsx              # Main app component
    │   ├── components/
    │   │   ├── AgentPanel.jsx   # AI Agents UI
    │   │   ├── Header.jsx
    │   │   └── ...
    │   └── services/
    │       └── api.js           # API client
    ├── public/
    ├── package.json
    └── vite.config.js
```

## 🧠 How RAG Works

### What is RAG?

RAG (Retrieval-Augmented Generation) makes AI analysis smarter by learning from your past applications. It uses **TF-IDF vectorization** (lightweight, no GPU needed) to build a searchable index.

### How It Helps

1. **Builds searchable index** of all applications
2. **Finds similar applications** when analyzing new emails
3. **Provides context to AI** for better extraction
4. **Improves over time** as you add more applications

### Example

**Without RAG:**
```
New email from "Google Careers"
AI: "Hmm, what company is this?"
→ May misidentify
```

**With RAG:**
```
New email from "Google Careers"
RAG: "You applied to Google before (Software Engineer)"
AI: "This is from Google, software role"
→ Better accuracy!
```

## 🔒 Security & Privacy

- **Credentials**: Never commit `credentials.json` or `token.pkl`
- **Local Processing**: All analysis happens on your machine
- **Read-Only Access**: App only reads emails, never modifies
- **No Cloud**: No data sent to external services (except Gmail API)
- **Agent Approval**: All agent actions require your approval

## 🎯 API Endpoints

### Email Scanning
- `GET /api/jobs` - Get all applications
- `GET /api/stats` - Get statistics
- `POST /api/scan` - Start email scan
- `GET /api/scan/status` - Check scan progress

### AI Agents
- `POST /api/agents/email/draft` - Draft email response
- `POST /api/agents/email/send` - Send approved email
- `POST /api/agents/research` - Research company
- `POST /api/agents/research/approve` - Get final report
- `POST /api/agents/interview-prep` - Create prep plan
- `POST /api/agents/interview-prep/approve` - Get final guide
- `GET /api/agents/status` - Check agent availability

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is open source and available under the MIT License.

## 🆘 Support

If you encounter issues:

1. Check the troubleshooting section above
2. Ensure all prerequisites are installed
3. Verify Ollama is running (`ollama serve`)
4. Check backend logs for errors
5. Hard refresh browser (Ctrl+Shift+R)

For additional help, create an issue with:
- Error messages
- Steps to reproduce
- System information (OS, Python version, Node version)
- Backend logs

## 🎉 Acknowledgments

- **Ollama** - Local AI inference
- **LangChain** - AI framework
- **LangGraph** - Agent state machines
- **React + Vite** - Modern UI framework
- **Flask** - Backend API
- **Gmail API** - Email access

---

**Built with ❤️ for making job hunting easier and smarter!**
