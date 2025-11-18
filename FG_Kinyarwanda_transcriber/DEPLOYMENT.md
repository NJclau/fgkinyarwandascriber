# 🚀 Kinyarwanda Focus Group Transcriber - Deployment Guide

Complete deployment instructions with admin authentication and user management.

## 📋 Table of Contents

1. [Quick Start (Local)](#quick-start-local)
2. [Production Deployment](#production-deployment)
3. [Admin Setup](#admin-setup)
4. [User Management Workflow](#user-management-workflow)
5. [Environment Configuration](#environment-configuration)
6. [Troubleshooting](#troubleshooting)

---

## 🏃 Quick Start (Local)

### Prerequisites
- Python 3.10+
- ffmpeg installed
- Google Gemini API key

### Installation Steps

```bash
# 1. Clone repository
git clone <your-repo-url>
cd kinyarwanda-transcriber/FG_Kinyarwanda_transcriber

# 2. Create virtual environment
python -m venv venv
source ven v/bin/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Install ffmpeg
# Ubuntu/Debian:
sudo apt-get install ffmpeg

# macOS:
brew install ffmpeg

# Windows: Download from https://ffmpeg.org/download.html

# 5. Configure secrets
mkdir .streamlit
cp src/config/secrets_template.example .streamlit/secrets.toml

# 6. Edit secrets.toml with your API keys
nano .streamlit/secrets.toml
```

### Configure `.streamlit/secrets.toml`

```toml
# API Keys
GEMINI_API_KEY = "your_gemini_api_key"

# Admin Configuration
ADMIN_EMAILS = [
    "admin@dinosoft.rw",
    "your_email@example.com"
]

# System Limits
MAX_FILE_SIZE_MB = 50
MAX_DURATION_MINUTES = 30
DAILY_UPLOAD_LIMIT = 10

# Optional: GPU Support
USE_GPU = false  # Set to true if GPU available
```

### Run Application

```bash
streamlit run app.py
```

Visit `http://localhost:8501`

---

## 🌐 Production Deployment

### Option 1: Streamlit Cloud (Recommended for MVP)

**Time:** 15 minutes | **Cost:** Free tier available

#### Steps:

1. **Prepare Repository**
```bash
# Add to .gitignore
echo ".streamlit/secrets.toml" >> .gitignore
echo "users_database.json" >> .gitignore
echo "pending_users.json" >> .gitignore
echo "usage_logs.json" >> .gitignore

# Commit and push
git add .
git commit -m "Initial deployment"
git push origin main
```

2. **Deploy to Streamlit Cloud**
- Visit https://share.streamlit.io
- Click "New app"
- Select your repository
- Main file: `app.py`
- Click "Deploy"

3. **Add Secrets**
- Go to App Settings → Secrets
- Paste your secrets.toml content:

```toml
# API Keys (Only Gemini needed - SpeechBrain downloads model automatically)
GEMINI_API_KEY = "your_gemini_key"

# Admin Configuration
ADMIN_EMAILS = [
    "admin@dinosoft.rw"
]

# System Limits
MAX_FILE_SIZE_MB = 50
MAX_DURATION_MINUTES = 30
DAILY_UPLOAD_LIMIT = 10

# Optional: GPU Support
USE_GPU = false
```

4. **Configure Settings**
- Python version: 3.10
- Resources: 2GB RAM recommended

---

### Option 2: Google Cloud Run (Production Scale)

**Time:** 1-2 hours | **Cost:** ~$20-50/month

#### Prerequisites
```bash
# Install Google Cloud SDK
gcloud auth login
gcloud config set project YOUR_PROJECT_ID
```

#### Deployment

1. **Create `Dockerfile`**
```dockerfile
FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy and install requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create data directories
RUN mkdir -p /app/data

EXPOSE 8080

# Health check
HEALTHCHECK CMD curl --fail http://localhost:8080/_stcore/health || exit 1

# Run app
CMD streamlit run app.py \
    --server.port=8080 \
    --server.address=0.0.0.0 \
    --server.headless=true
```

2. **Build and Deploy**
```bash
# Build image
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/kinyarwanda-transcriber

# Deploy to Cloud Run
gcloud run deploy kinyarwanda-transcriber \
  --image gcr.io/YOUR_PROJECT_ID/kinyarwanda-transcriber \
  --region us-central1 \
  --platform managed \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 2 \
  --timeout 3600 \
  --set-env-vars GEMINI_API_KEY=your_key,USE_GPU=false
```

3. **Configure Persistent Storage (Optional)**
```bash
# Create Cloud Storage bucket for user database
gcloud storage buckets create gs://kinyarwanda-transcriber-data \
  --location=us-central1

# Update app to use Cloud Storage for JSON files
```

---

## 🔐 Admin Setup

### Initial Admin Configuration

1. **Set Admin Emails in secrets.toml**
```toml
ADMIN_EMAILS = [
    "claude.nshime@dinosoft.rw",
    "admin2@dinosoft.rw"
]
```

2. **First Admin Login**
- Visit your deployed app
- Login with your admin email
- Access Admin Dashboard from sidebar

### Admin Dashboard Features

#### 👥 User Management
- View all active users
- See usage statistics per user
- Revoke access when needed
- Export user database

#### ⏳ Pending Requests
- Review access requests
- Approve/reject with reasons
- Email notifications (when configured)

#### 📊 Usage Analytics
- Total transcriptions
- Duration tracking
- User activity logs
- Export reports

#### ⚙️ System Settings
- Configure upload limits
- Set rate limits
- Database management
- System backups

---

## 👥 User Management Workflow

### For Users (Focus Group Members)

1. **Request Access**
   - Visit app URL
   - Click "Request Access" tab
   - Fill in:
     - Email address
     - Full name
     - Organization
     - Reason for access
   - Submit request

2. **Wait for Approval**
   - Admin reviews request
   - Receives approval notification
   - Can now login

3. **Login and Use**
   - Enter approved email
   - Click Login
   - Upload and process audio files

### For Admins

1. **Review Requests**
   - Login with admin email
   - Go to Admin Dashboard
   - Check "Pending Requests" tab

2. **Approve Users**
   - Review user information
   - Click "Approve" for valid requests
   - User can now access system

3. **Manage Users**
   - Monitor usage in "Usage Analytics"
   - Revoke access if needed
   - Export reports for compliance

---

## ⚙️ Environment Configuration

### Required Environment Variables

| Variable | Description | Required | Example |
|----------|-------------|----------|---------|
| `GEMINI_API_KEY` | Google Gemini API key | Yes | `AIzaSy...` |
| `ADMIN_EMAILS` | List of admin emails | Yes | `["admin@example.com"]` |
| `MAX_FILE_SIZE_MB` | Max upload size | No | `50` |
| `MAX_DURATION_MINUTES` | Max audio duration | No | `30` |
| `DAILY_UPLOAD_LIMIT` | Uploads per user/day | No | `10` |
| `USE_GPU` | Enable GPU acceleration | No | `false` |

### Optional: Email Notifications

To enable email notifications for access requests:

```toml
# Add to secrets.toml
[email]
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_EMAIL = "noreply@dinosoft.rw"
SMTP_PASSWORD = "your_app_password"
```

Update `src/services/admin_handler.py` to send emails on approval/rejection.

---

## 🔧 Troubleshooting

### Common Issues

#### 1. Model Loading Fails
```bash
# SpeechBrain downloads model automatically on first run
# Verify internet connection
ping huggingface.co

# Check disk space (model is ~400MB)
df -h

# If download fails, clear cache and retry:
rm -rf pretrained_models/
```

#### 2. Audio Processing Errors
```bash
# Verify ffmpeg installation
ffmpeg -version

# Check audio file format
ffprobe your_audio_file.mp3
```

#### 3. Gemini API Errors
```bash
# Test API key
curl -H "Content-Type: application/json" \
  -d '{"contents":[{"parts":[{"text":"test"}]}]}' \
  "https://generativelanguage.googleapis.com/v1/models/gemini-pro:generateContent?key=YOUR_KEY"
```

#### 4. Database Permissions
```bash
# Ensure write permissions
chmod 666 users_database.json
chmod 666 pending_users.json
chmod 666 usage_logs.json
```

#### 5. Streamlit Cloud Issues
- Check app logs in Streamlit Cloud dashboard
- Verify secrets are correctly configured
- Ensure Python version is 3.10
- Check resource limits (upgrade if needed)

### Performance Optimization

```python
# Cache model loading
@st.cache_resource
def load_transcriber():
    from src.core.transcriber import KinyarwandaTranscriber
    transcriber = KinyarwandaTranscriber()
    transcriber.load_model()
    return transcriber

# Cache Gemini processor
@st.cache_resource
def load_gemini():
    from src.core.gemini_processor import GeminiProcessor
    return GeminiProcessor()
```

---

## 📊 Monitoring & Maintenance

### Daily Tasks
- Review pending access requests
- Check usage analytics
- Monitor error logs

### Weekly Tasks
- Export usage reports
- Backup user database
- Review system performance

### Monthly Tasks
- Audit user access
- Analyze usage patterns
- Update documentation
- Review API quotas

---

## 🔒 Security Best Practices

1. **API Keys**
   - Never commit secrets to git
   - Rotate keys quarterly
   - Use environment-specific keys

2. **User Access**
   - Review users monthly
   - Revoke inactive accounts
   - Monitor for abuse

3. **Data Privacy**
   - Don't log sensitive audio content
   - Implement data retention policy
   - Comply with GDPR/data regulations

4. **System Security**
   - Keep dependencies updated
   - Enable HTTPS in production
   - Implement rate limiting
   - Log security events

---

## 📝 Support & Resources

- **Documentation:** This guide
- **Issues:** GitHub Issues
- **Contact:** claude.nshime@dinosoft.rw
- **Streamlit Docs:** https://docs.streamlit.io
- **HuggingFace:** https://huggingface.co/docs
- **Gemini API:** https://ai.google.dev/docs

---

## 🎯 Next Steps

After successful deployment:

1. ✅ Login as admin
2. ✅ Test full transcription workflow
3. ✅ Invite first focus group members
4. ✅ Set up monitoring alerts
5. ✅ Schedule regular backups
6. ✅ Document internal procedures

---

**Last Updated:** November 2025  
**Maintained by:** DinoSoft Engineering Team  
**Version:** 2.0.0
