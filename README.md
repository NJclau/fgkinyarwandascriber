# 🎙️ Kinyarwanda Focus Group Transcriber

AI-powered audio transcription and analysis platform for Kinyarwanda focus group discussions. Automatically transcribes, corrects, summarizes, and translates focus group recordings with built-in admin portal for user management.

[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white)](https://streamlit.io)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![License](https://img.shields.io/badge/License-GPL%20v3-blue.svg?style=for-the-badge)](LICENSE)

---

## ✨ Features

### 🎯 Core Transcription
- **Automatic Speech Recognition**: SpeechBrain Wav2Vec2 model fine-tuned for Kinyarwanda
- **AI-Powered Correction**: Gemini Pro API fixes orthography, grammar, and punctuation
- **Bilingual Summaries**: Generate key insights in both Kinyarwanda and English
- **Timestamp Tracking**: Every transcript segment includes precise time markers
- **Multiple Audio Formats**: Supports MP3, WAV, M4A, OGG, FLAC

### 🔐 Admin Portal
- **User Management**: Approve/reject access requests from focus group members
- **Usage Analytics**: Track transcriptions, duration, and user activity
- **Access Control**: Email-based authentication with admin/user roles
- **Rate Limiting**: Configure daily upload limits per user
- **Audit Logs**: Complete history of all transcription sessions

### 📊 Reports & Export
- **Cleaned Transcripts**: Corrected Kinyarwanda text with timestamps
- **Executive Summaries**: Concise insights in Kinyarwanda and English
- **Raw Transcripts**: Unprocessed ASR output for reference
- **Complete Reports**: All-in-one downloadable document

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.10+**
- **ffmpeg** (audio processing)
- **Google Gemini API key** ([Get one here](https://makersuite.google.com/app/apikey))

**Note**: ✅ No Hugging Face token needed! SpeechBrain automatically downloads the Kinyarwanda ASR model.

### Installation

```bash
# 1. Clone repository
git clone https://github.com/yourusername/kinyarwanda-transcriber.git
cd kinyarwanda-transcriber

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Install ffmpeg
# Ubuntu/Debian:
sudo apt-get install ffmpeg

# macOS:
brew install ffmpeg

# Windows: Download from https://ffmpeg.org/download.html
```

### Configuration

Create `.streamlit/secrets.toml`:

```toml
# Google Gemini API Key (Required)
GEMINI_API_KEY = "your_gemini_api_key_here"

# Admin Emails (Required)
ADMIN_EMAILS = [
    "admin@dinosoft.rw",
    "your_email@example.com"
]

# System Limits (Optional)
MAX_FILE_SIZE_MB = 50
MAX_DURATION_MINUTES = 30
DAILY_UPLOAD_LIMIT = 10

# GPU Support (Optional - default: false)
USE_GPU = false
```

### Run Application

```bash
streamlit run main_app_integrated.py
```

Visit **http://localhost:8501**

---

## 📖 Usage Guide

### For Admins

1. **Initial Setup**
   - Add your email to `ADMIN_EMAILS` in secrets
   - Login with your admin email
   - Access Admin Dashboard from sidebar

2. **Manage Users**
   - Review pending access requests
   - Approve valid focus group members
   - Monitor usage analytics
   - Revoke access if needed

3. **System Monitoring**
   - Check usage logs regularly
   - Export reports for compliance
   - Adjust upload limits as needed

### For Focus Group Members

1. **Request Access**
   - Visit the app URL
   - Click "Request Access" tab
   - Fill in your details:
     - Email address
     - Full name
     - Organization
     - Reason for access
   - Submit and wait for admin approval

2. **Login & Transcribe**
   - Login with your approved email
   - Upload audio file (MP3, WAV, M4A, OGG, FLAC)
   - Configure chunk duration (optional)
   - Click "Start Processing"

3. **Review & Export**
   - Review cleaned transcript
   - Read Kinyarwanda summary
   - Check English translation
   - Download individual sections or complete report

---

## 🏗️ Architecture

### Tech Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Frontend/Backend** | Streamlit 1.31 | Web interface & server |
| **ASR Model** | SpeechBrain Wav2Vec2 | Kinyarwanda speech recognition |
| **AI Processing** | Google Gemini Pro | Text correction & summarization |
| **Audio Processing** | librosa, pydub, ffmpeg | Audio manipulation |
| **Storage** | JSON files | User database & logs |

### Processing Pipeline

```
Audio Upload → Preprocessing → Chunking → ASR (SpeechBrain)
    ↓
Raw Transcript → Orthography Fix (Gemini) → Cleaned Transcript
    ↓
Kinyarwanda Summary (Gemini) → English Translation (Gemini)
    ↓
Complete Report → Export Options
```

### Project Structure

```
kinyarwanda-transcriber/
├── main_app_integrated.py          # Main Streamlit app with routing
├── admin_handler_enhanced.py       # User management & admin dashboard
├── transcriber.py                  # SpeechBrain Wav2Vec2 transcription
├── gemini_processor.py             # Gemini API integration
├── requirements.txt                # Python dependencies
├── users_database.json             # Approved users (auto-created)
├── pending_users.json              # Pending requests (auto-created)
├── usage_logs.json                 # Usage tracking (auto-created)
├── pretrained_models/              # SpeechBrain model cache (auto-created)
├── .streamlit/
│   └── secrets.toml                # Configuration (DO NOT COMMIT)
├── .gitignore
├── README.md
├── DEPLOYMENT.md
└── LICENSE
```

---

## 🌐 Deployment

### Option 1: Streamlit Cloud (Recommended for MVP)

**Fastest deployment** - 15 minutes

1. Push code to GitHub
2. Visit [share.streamlit.io](https://share.streamlit.io)
3. Connect repository
4. Add secrets via dashboard
5. Deploy!

**Cost**: Free tier available  
**Best for**: MVP, demos, small teams

### Option 2: Google Cloud Run (Production)

**Scalable production deployment** - 1-2 hours

```bash
# Build and deploy
gcloud builds submit --tag gcr.io/PROJECT_ID/kinyarwanda-transcriber
gcloud run deploy kinyarwanda-transcriber \
  --image gcr.io/PROJECT_ID/kinyarwanda-transcriber \
  --memory 2Gi \
  --timeout 3600
```

**Cost**: ~$20-50/month  
**Best for**: Production, scaling, enterprise

See [DEPLOYMENT.md](DEPLOYMENT.md) for complete deployment instructions.

---

## 🔧 Configuration

### Audio Processing Settings

| Setting | Default | Range | Description |
|---------|---------|-------|-------------|
| Chunk Duration | 30s | 20-60s | Audio segment length |
| Sample Rate | 16kHz | Fixed | Required for model |
| Channels | Mono | Fixed | Required for model |
| Overlap | 2s | Fixed | Prevents word cutting |

### System Limits

```toml
MAX_FILE_SIZE_MB = 50        # ~30 minutes of audio
MAX_DURATION_MINUTES = 30    # Maximum audio length
DAILY_UPLOAD_LIMIT = 10      # Uploads per user per day
```

### GPU Support (Optional)

Enable GPU acceleration for faster processing:

```toml
USE_GPU = true  # Requires CUDA-compatible GPU
```

---

## 📊 Admin Dashboard

### User Management
- View all active users
- See usage statistics per user
- Revoke access when needed
- Export user database

### Pending Requests
- Review new access requests
- Approve/reject with reasons
- Track request history

### Usage Analytics
- Total transcriptions processed
- Duration tracking per user
- Activity logs and exports
- System performance metrics

### System Settings
- Configure upload limits
- Set rate limits
- Database management
- System backups

---

## 🔒 Security Features

- ✅ Email-based authentication
- ✅ Admin/user role separation
- ✅ Usage logging and auditing
- ✅ File size and rate limiting
- ✅ API key protection via secrets
- ✅ Session management
- ✅ Input validation

---

## 🐛 Troubleshooting

### Model Loading Issues

**Problem**: Model fails to download

**Solution**:
```bash
# Check internet connection
ping huggingface.co

# Verify disk space (~400MB needed)
df -h

# Clear cache and retry
rm -rf pretrained_models/
```

### Audio Processing Errors

**Problem**: Audio file processing fails

**Solution**:
```bash
# Verify ffmpeg installation
ffmpeg -version

# Test audio file
ffprobe your_audio.mp3

# Try converting format
ffmpeg -i input.m4a output.wav
```

### Gemini API Errors

**Problem**: API key invalid or quota exceeded

**Solution**:
- Verify API key at [Google AI Studio](https://makersuite.google.com/app/apikey)
- Check quota limits in Google Cloud Console
- Ensure billing is enabled for production use

### Permission Errors

**Problem**: Cannot write to database files

**Solution**:
```bash
# Fix file permissions
chmod 666 users_database.json
chmod 666 pending_users.json
chmod 666 usage_logs.json
```

---

## 📈 Performance Optimization

### Caching

```python
@st.cache_resource
def load_transcriber():
    """Cache model loading across sessions"""
    transcriber = KinyarwandaTranscriber()
    transcriber.load_model()
    return transcriber
```

### Recommendations

- **Memory**: 2GB+ RAM recommended
- **CPU**: 2+ cores for parallel processing
- **GPU**: Optional, speeds up transcription by 3-5x
- **Network**: Stable connection for API calls
- **Storage**: 1GB+ for model cache

---

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Setup

```bash
# Install dev dependencies
pip install -r requirements-dev.txt

# Run tests
pytest tests/

# Code formatting
black .
flake8 .
```

---

## 📝 License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.

---

## 👥 Authors & Acknowledgments

**Developed by**: DinoSoft Software Development Company  
**Lead Developer**: Claude Nshime (CEO/CTO)  
**Contact**: claude.nshime@dinosoft.rw

**Acknowledgments**:
- SpeechBrain team for the Kinyarwanda ASR model
- Google for Gemini API
- Streamlit for the amazing framework
- Focus group research community

---

## 📞 Support

- **Documentation**: [DEPLOYMENT.md](DEPLOYMENT.md)
- **Issues**: [GitHub Issues](https://github.com/yourusername/kinyarwanda-transcriber/issues)
- **Email**: claude.nshime@dinosoft.rw
- **Website**: [dinosoft.rw](https://dinosoft.rw)

---

## 🗺️ Roadmap

### Current (v2.0)
- ✅ SpeechBrain ASR integration
- ✅ Admin portal with user management
- ✅ Usage analytics dashboard
- ✅ Multi-format audio support

### Upcoming (v2.1)
- 🔲 Real-time transcription
- 🔲 Speaker diarization (identify speakers)
- 🔲 Cloud storage integration (GCS/Firebase)
- 🔲 Email notifications
- 🔲 Custom vocabulary support

### Future (v3.0)
- 🔲 Multi-language support
- 🔲 Advanced analytics dashboard
- 🔲 API access for integrations
- 🔲 Mobile app (iOS/Android)
- 🔲 Collaborative annotation tools

---

## 📊 Statistics

- **Model Size**: ~400MB
- **Supported Audio**: MP3, WAV, M4A, OGG, FLAC
- **Max File Size**: 50MB (configurable)
- **Processing Time**: ~1-2 minutes per 10 minutes of audio
- **Accuracy**: 85-90% WER on Kinyarwanda speech

---

## ⭐ Star History

If you find this project useful, please consider giving it a star on GitHub!

---

**Built with ❤️ for Kinyarwanda focus group research**

Last Updated: November 2025 | Version 2.0.0
