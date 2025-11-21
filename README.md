# Job Tracker - Email Scanner & Application Manager

A smart job application tracker that automatically scans your Gmail for job-related emails and organizes them using AI analysis. Built with Flask, Gmail API, and Ollama AI.

## 🌟 Features

- **Automatic Email Scanning**: Scans Gmail for job applications, confirmations, and responses
- **AI-Powered Analysis**: Uses Ollama (llama3.2:3b) to categorize and extract job information
- **Real-time Web Interface**: Modern web UI with progress tracking
- **Smart Filtering**: Filters by status (Applied, Interview, Offer, etc.)
- **Database Storage**: SQLite database to track all applications
- **Customizable Search**: Configurable keywords and date ranges

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
# Install the lightweight model (recommended)
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

### 6. Set Up React Frontend (Optional - Modern UI)

```bash
# Navigate to the React frontend directory
cd job-tracker

# Install Node.js dependencies
npm install

# Start the development server
npm run dev
```

The React frontend will run on **http://localhost:5173** (Vite default port)

### 7. Start the Flask Backend

```bash
# From the main project directory
python app.py
```

The Flask API will run on **http://localhost:5000**

**Note**: You can use either:
- **Modern React UI**: http://localhost:5173 (recommended - better UX)
- **Legacy HTML UI**: http://localhost:5000 (simple, works without Node.js)

## 🔧 Configuration

### Email Keywords
Edit `config.py` to customize job-related keywords:

```python
JOB_KEYWORDS = [
    "application", "applied", "position", "role", "job",
    "interview", "assessment", "opportunity", "linkedin",
    "thank you for applying", "application received",
    "noreply", "jobs-noreply", "recruiting"
]
```

### AI Model Selection
In `ai_analyzer.py`, you can change the model:

```python
MODEL_NAME = "llama3.2:3b"  # Fast, lightweight
# MODEL_NAME = "mistral:7b"  # Slower but more accurate
```

### Scan Period
Default scan looks back 60 days. Change in `config.py`:

```python
DEFAULT_DAYS_BACK = 60  # Adjust as needed
```

## 📱 Usage

1. **Launch the Web Interface**:
   - React UI: Visit http://localhost:5173 (run `npm run dev` in job-tracker/)
   - Legacy UI: Visit http://localhost:5000
2. **Start Scanning**: Click "Launch Scan" button
3. **Choose Time Range**: Select from 5 days to 120 days back
4. **Monitor Progress**: Real-time progress bar and status updates
5. **Review Results**: Filter by status, update applications, add notes

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
```

#### "Gmail API not enabled"
- Ensure Gmail API is enabled in Google Cloud Console
- Check that `credentials.json` is in the project root
- Verify OAuth consent screen is configured

#### Slow AI Analysis
- Switch to faster model: `MODEL_NAME = "llama3.2:3b"`
- The app shows "may take 1-2 min per email" - this is normal
- Progress updates every email processed

#### No Emails Found
- Check date range (try more days back)
- Verify keywords in `config.py` match your emails
- Ensure Gmail account has job-related emails in the specified period

### Performance Tips

- **Use llama3.2:3b** for faster analysis (recommended)
- **Scan shorter periods** first (5-30 days) to test
- **Run during off-peak hours** for better AI performance
- **Close other heavy applications** while scanning

## 🗂 Project Structure

```
Job_Tracker/
├── app.py                 # Flask web application (backend API)
├── email_fetcher.py       # Gmail API integration
├── ai_analyzer.py         # Ollama AI analysis
├── database.py           # SQLite database operations
├── config.py             # Configuration settings
├── credentials.json      # Gmail API credentials (you create this)
├── token.pkl            # Gmail auth token (auto-generated)
├── requirements.txt     # Python dependencies
├── job_tracker.db       # SQLite database (auto-generated)
├── frontend/            # Legacy HTML frontend
│   └── index.html
└── job-tracker/         # Modern React frontend
    ├── src/            # React components
    ├── public/         # Static assets
    ├── package.json    # Node dependencies
    └── vite.config.js  # Vite configuration
```

## 🔒 Security & Privacy

- **Credentials**: Never commit `credentials.json` or `token.pkl` to version control
- **Local Processing**: All email analysis happens locally on your machine
- **Read-Only Access**: App only reads emails, never modifies or sends
- **No Data Sharing**: Your email data stays on your computer

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📝 License

This project is open source and available under the MIT License.

## 🆘 Support

If you encounter issues:

1. Check the troubleshooting section above
2. Ensure all prerequisites are installed
3. Verify authentication is working
4. Check that Ollama service is running
5. Look at console logs for specific error messages

For additional help, create an issue in the GitHub repository with:
- Error messages
- Steps to reproduce
- Your system information (OS, Python version)