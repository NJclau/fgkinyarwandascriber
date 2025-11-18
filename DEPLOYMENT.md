# Deployment Guide

Complete deployment instructions for Kinyarwanda Focus Group Transcriber across multiple platforms.

## Table of Contents

1. [Streamlit Cloud (Fastest)](#streamlit-cloud)
2. [Google Cloud Run (Production)](#google-cloud-run)
3. [Docker Deployment](#docker-deployment)
4. [Google OAuth Setup](#google-oauth-setup)
5. [Cloud Storage Integration](#cloud-storage)
6. [Monitoring & Logging](#monitoring)

---

## Streamlit Cloud

**Best for**: MVP, demos, small teams  
**Time to deploy**: 15 minutes  
**Cost**: Free tier available

### Steps

1. **Prepare Repository**
```bash
# Create .gitignore
echo ".streamlit/secrets.toml" >> .gitignore
echo "__pycache__/" >> .gitignore
echo "*.pyc" >> .gitignore

# Commit code
git add .
git commit -m "Initial commit"
git push origin main
```

2. **Deploy to Streamlit Cloud**
- Visit https://share.streamlit.io
- Click "New app"
- Select your GitHub repository
- Set main file: `app.py`
- Click "Deploy"

3. **Add Secrets**
- Go to App Settings → Secrets
- Paste your `secrets.toml` content:
```toml
HF_TOKEN = "hf_your_token"
GEMINI_API_KEY = "your_gemini_key"
DEMO_MODE = true
```

4. **Configure Advanced Settings**
- Python version: 3.10
- Enable "Always rerun on save" for development

### Custom Domain (Optional)
- Go to Settings → General
- Add custom domain
- Update DNS CNAME record

---

## Google Cloud Run

**Best for**: Production, scalability, enterprise  
**Time to deploy**: 1-2 hours  
**Cost**: Pay per use (~$0.40/hour active)

### Prerequisites
```bash
# Install Google Cloud SDK
# Visit: https://cloud.google.com/sdk/docs/install

gcloud auth login
gcloud config set project YOUR_PROJECT_ID
```

### Method 1: Automatic Deploy

1. **Create app.yaml**
```yaml
runtime: python310
entrypoint: streamlit run app.py --server.port=$PORT --server.address=0.0.0.0

env_variables:
  HF_TOKEN: "your_token"
  GEMINI_API_KEY: "your_key"
  DEMO_MODE: "true"
```

2. **Deploy**
```bash
gcloud run deploy kinyarwanda-transcriber \
  --source . \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 2 \
  --timeout 3600
```

### Method 2: Docker Deploy

1. **Create Dockerfile**
```dockerfile
FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK CMD curl --fail http://localhost:8080/_stcore/health || exit 1

# Run app
CMD streamlit run app.py \
    --server.port=8080 \
    --server.address=0.0.0.0 \
    --server.headless=true \
    --browser.serverAddress="0.0.0.0" \
    --server.enableCORS=false
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
  --set-env-vars HF_TOKEN=your_token,GEMINI_API_KEY=your_key
```

### Environment Variables
```bash
# Set secrets via Secret Manager
gcloud secrets create hf-token --data-file=- <<< "hf_your_token"
gcloud secrets create gemini-key --data-file=- <<< "your_gemini_key"

# Grant access to Cloud Run
gcloud secrets add-iam-policy-binding hf-token \
  --member=serviceAccount:PROJECT_NUMBER-compute@developer.gserviceaccount.com \
  --role=roles/secretmanager.secretAccessor
```

---

## Docker Deployment

**Best for**: Self-hosting, on-premise  
**Time to deploy**: 30 minutes

### Local Docker

```bash
# Build
docker build -t kinyarwanda-transcriber .

# Run
docker run -p 8501:8080 \
  -e HF_TOKEN=your_token \
  -e GEMINI_API_KEY=your_key \
  kinyarwanda-transcriber
```

### Docker Compose

**docker-compose.yml**
```yaml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8501:8080"
    environment:
      - HF_TOKEN=${HF_TOKEN}
      - GEMINI_API_KEY=${GEMINI_API_KEY}
      - DEMO_MODE=false
    volumes:
      - ./data:/app/data
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/_stcore/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

**Deploy**
```bash
# Create .env file
cat > .env << EOF
HF_TOKEN=your_token
GEMINI_API_KEY=your_key
EOF

# Start
docker-compose up -d

# View logs
docker-compose logs -f
```

---

## Google OAuth Setup

**Required for**: Production authentication

### 1. Google Cloud Console

1. Go to https://console.cloud.google.com
2. Select/Create project
3. Enable APIs:
   - Google+ API
   - People API

4. Create OAuth Credentials:
   - Navigation menu → APIs & Services → Credentials
   - Create Credentials → OAuth 2.0 Client ID
   - Application type: Web application
   - Name: Kinyarwanda Transcriber

5. **Authorized redirect URIs**:
```
http://localhost:8501
https://your-app.streamlit.app
https://your-domain.com
```

6. Copy Client ID and Client Secret

### 2. Update Code

**Install package**
```bash
pip install streamlit-google-oauth
```

**Update requirements.txt**
```
streamlit-google-oauth==0.1.7
```

**Update auth_handler.py**
```python
from streamlit_google_auth import Authenticate

def check_authentication() -> bool:
    authenticator = Authenticate(
        secret_credentials_path='.streamlit/secrets.toml',
        cookie_name='focus_group_auth',
        cookie_key=st.secrets["COOKIE_KEY"],
        redirect_uri=st.secrets["google_oauth"]["redirect_uri"]
    )
    
    authenticator.check_authentification()
    
    if authenticator.is_authentificated:
        st.session_state.authenticated = True
        st.session_state.user_email = authenticator.user_email
        st.session_state.user_name = authenticator.user_name
        return True
    
    return False
```

**Update secrets.toml**
```toml
[google_oauth]
client_id = "your-id.apps.googleusercontent.com"
client_secret = "your-secret"
redirect_uri = "https://your-app.streamlit.app"

COOKIE_KEY = "random_secure_key_here"
DEMO_MODE = false

ALLOWED_EMAILS = [
    "researcher1@example.com",
    "researcher2@example.com"
]
```

### 3. Add Email Whitelist (Optional)

**Update auth_handler.py**
```python
def check_authentication() -> bool:
    authenticator = Authenticate(...)
    authenticator.check_authentification()
    
    if authenticator.is_authentificated:
        # Check whitelist
        allowed = st.secrets.get("ALLOWED_EMAILS", [])
        if allowed and authenticator.user_email not in allowed:
            st.error("Access denied. Contact admin.")
            return False
        
        st.session_state.authenticated = True
        st.session_state.user_email = authenticator.user_email
        return True
    
    return False
```

---

## Cloud Storage

**Best for**: Storing audio files and transcripts persistently

### Google Cloud Storage

**Setup**
```bash
# Create bucket
gcloud storage buckets create gs://kinyarwanda-transcriber-data \
  --location=us-central1 \
  --uniform-bucket-level-access

# Create service account
gcloud iam service-accounts create transcriber-sa

# Grant permissions
gcloud storage buckets add-iam-policy-binding gs://kinyarwanda-transcriber-data \
  --member="serviceAccount:transcriber-sa@PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/storage.objectAdmin"

# Create key
gcloud iam service-accounts keys create key.json \
  --iam-account=transcriber-sa@PROJECT_ID.iam.gserviceaccount.com
```

**Integration**
```python
# Add to requirements.txt
google-cloud-storage==2.14.0

# storage_handler.py
from google.cloud import storage
import streamlit as st

def upload_audio(file_path: str, bucket_name: str):
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(f"audio/{os.path.basename(file_path)}")
    blob.upload_from_filename(file_path)
    return blob.public_url

def save_transcript(content: str, filename: str, bucket_name: str):
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(f"transcripts/{filename}")
    blob.upload_from_string(content)
```

### Firebase Storage (Alternative)

```bash
pip install firebase-admin
```

**firebase_config.py**
```python
import firebase_admin
from firebase_admin import credentials, storage

cred = credentials.Certificate('firebase-key.json')
firebase_admin.initialize_app(cred, {
    'storageBucket': 'your-project.appspot.com'
})

bucket = storage.bucket()
```

---

## Monitoring

### Streamlit Cloud Logs
- Dashboard → Manage app → Logs
- Real-time log streaming
- Error tracking

### Google Cloud Logging

```bash
# View logs
gcloud logging read "resource.type=cloud_run_revision" --limit 50

# Set up alerts
gcloud alpha monitoring policies create \
  --notification-channels=CHANNEL_ID \
  --display-name="Transcriber Errors" \
  --condition-threshold-value=5 \
  --condition-threshold-duration=300s
```

### Application Monitoring

**Add to app.py**
```python
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Log usage
logger.info(f"User {st.session_state.user_email} uploaded {audio_file.name}")
logger.info(f"Processing time: {process_time:.2f}s")
```

---

## Performance Optimization

### Caching
```python
@st.cache_resource
def load_transcriber():
    transcriber = KinyarwandaTranscriber()
    transcriber.load_model()
    return transcriber

@st.cache_data
def process_audio_cached(audio_path, chunk_duration):
    return transcriber.transcribe_audio(audio_path, chunk_duration)
```

### Resource Limits
```yaml
# Cloud Run
--memory 2Gi
--cpu 2
--timeout 3600
--concurrency 10
--max-instances 5
```

---

## Security Checklist

- [ ] Secrets stored securely (not in code)
- [ ] HTTPS enabled in production
- [ ] OAuth configured with authorized domains
- [ ] API rate limiting implemented
- [ ] Input validation on file uploads
- [ ] Session timeouts configured
- [ ] CORS properly configured
- [ ] Error messages don't leak sensitive info
- [ ] Audit logging enabled
- [ ] Regular dependency updates

---

## Cost Optimization

### Streamlit Cloud
- Free tier: 1 app, community support
- Team plan: $250/month (5 apps)

### Google Cloud Run
- Free tier: 2M requests/month
- Estimated cost: $10-50/month for moderate use
- Optimize: Use smaller instances, implement caching

### API Costs
- Gemini API: Free tier available
- HuggingFace: Free for inference
- Monitor quotas regularly

---

## Troubleshooting

**Build failures**
```bash
# Check logs
gcloud builds log $(gcloud builds list --limit=1 --format='value(id)')
```

**Memory issues**
- Increase `--memory` flag
- Implement audio chunking
- Clear cache between runs

**Timeout errors**
- Increase `--timeout`
- Process audio in smaller chunks
- Use async processing

**OAuth redirect issues**
- Verify redirect URI matches exactly
- Check authorized domains in GCP console
- Clear browser cookies

---

## Support & Resources

- Streamlit Docs: https://docs.streamlit.io
- Cloud Run Docs: https://cloud.google.com/run/docs
- Gemini API: https://ai.google.dev/docs
- HuggingFace: https://huggingface.co/docs

---

**Last Updated**: November 2025  
**Maintained by**: DinoSoft Engineering Team
