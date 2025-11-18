# 🎙️ Kinyarwanda Focus Group Transcriber

AI-powered audio transcription and analysis for Kinyarwanda focus group discussions. Automatically transcribes, corrects, summarizes, and translates focus group recordings.

## Features

- **Automatic Speech Recognition**: Wav2Vec2 model fine-tuned for Kinyarwanda
- **AI-Powered Correction**: Gemini API fixes orthography, grammar, and punctuation
- **Bilingual Summaries**: Key insights in both Kinyarwanda and English
- **Timestamp Tracking**: Every transcript segment includes time markers
- **Secure Authentication**: Google OAuth integration ready
- **Export Options**: Download transcripts and summaries in multiple formats

## Tech Stack

- **Frontend/Backend**: Streamlit
- **ASR Model**: Wav2Vec2 (Hugging Face)
- **AI Processing**: Google Gemini Pro
- **Audio Processing**: librosa, pydub, ffmpeg

## Quick Start

### Prerequisites

- Python 3.10+
- ffmpeg installed
- Hugging Face account + token
- Google Gemini API key

### Installation

1. **Clone repository**
```bash
git clone https://github.com/yourusername/kinyarwanda-transcriber.git
cd kinyarwanda-transcriber
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Install ffmpeg**
```bash
# Ubuntu/Debian
sudo apt-get install ffmpeg

# macOS
brew install ffmpeg

# Windows
# Download from https://ffmpeg.org/download.html
```

4. **Configure secrets**
```bash
mkdir .streamlit
cp secrets.toml.example .streamlit/secrets.toml
```

Edit `.streamlit/secrets.toml`:
```toml
HF_TOKEN = "hf_your_token_here"
GEMINI_API_KEY = "your_gemini_key_here"
DEMO_MODE = true
```

5. **Run application**
```bash
streamlit run app.py
```

Visit `http://localhost:8501`

## Usage

1. **Login**: Click "Login with Google" (demo mode auto-authenticates)
2. **Upload**: Select audio file (MP3, WAV, M4A, OGG, FLAC)
3. **Process**: Click "Start Processing" and wait for pipeline completion
4. **Review**: View cleaned transcript, Kinyarwanda summary, and English translation
5. **Export**: Download individual sections or complete report

## Project Structure

```
kinyarwanda-transcriber/
├── app.py                    # Main Streamlit application
├── transcriber.py            # Wav2Vec2 transcription engine
├── gemini_processor.py       # Gemini API integration
├── auth_handler.py           # Authentication logic
├── requirements.txt          # Python dependencies
├── .streamlit/
│   └── secrets.toml         # API keys (DO NOT COMMIT)
├── README.md
└── DEPLOYMENT.md
```

## API Keys Setup

### Hugging Face Token
1. Go to https://huggingface.co/settings/tokens
2. Create new token with "Read" access
3. Add to `secrets.toml` as `HF_TOKEN`

### Google Gemini API
1. Visit https://makersuite.google.com/app/apikey
2. Create API key
3. Add to `secrets.toml` as `GEMINI_API_KEY`

## Configuration

### Audio Processing
- Default chunk duration: 30 seconds (adjustable in sidebar)
- Supported formats: MP3, WAV, M4A, OGG, FLAC
- Automatic resampling to 16kHz mono

### Authentication
- Demo mode enabled by default
- Production OAuth setup in `auth_handler.py`
- See `DEPLOYMENT.md` for Google OAuth configuration

## Development

### Run in development mode
```bash
streamlit run app.py --server.runOnSave true
```

### Add new features
1. Update relevant module (`transcriber.py`, `gemini_processor.py`, etc.)
2. Test locally
3. Commit changes
4. Deploy to Streamlit Cloud (auto-deploys on push)

## Troubleshooting

**Model loading fails**
- Verify HF_TOKEN is valid
- Check internet connection
- Try fallback model (automatic)

**Audio processing errors**
- Ensure ffmpeg is installed: `ffmpeg -version`
- Verify audio file format is supported
- Check file isn't corrupted

**Gemini API errors**
- Confirm API key is active
- Check quota limits at https://console.cloud.google.com
- Review rate limiting in `gemini_processor.py`

## Security & Compliance

- API keys stored in secrets (never in code)
- Demo mode for development/testing
- Production OAuth ready for deployment
- Session management with timeouts
- Audit logging capability

## Contributing

1. Fork repository
2. Create feature branch
3. Make changes
4. Test thoroughly
5. Submit pull request

## License

MIT License - see LICENSE file

## Support

- Documentation: See `DEPLOYMENT.md` for deployment guides
- Issues: Open GitHub issue with error logs
- Contact: focusgroup@dinosoft.rw

## Roadmap

- [ ] Multi-user collaboration
- [ ] Cloud storage integration (GCS/Firebase)
- [ ] Real-time transcription
- [ ] Speaker diarization
- [ ] Custom vocabulary support
- [ ] Advanced analytics dashboard

---

Built with ❤️ for Kinyarwanda focus group research
