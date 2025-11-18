import streamlit as st
import os
import tempfile
from datetime import datetime
from transcriber import KinyarwandaTranscriber
from gemini_processor import GeminiProcessor
from auth_handler import check_authentication
from admin_handler import AdminHandler, render_admin_dashboard

# Page config
st.set_page_config(
    page_title="Kinyarwanda Focus Group Transcriber",
    page_icon="🎙️",
    layout="wide"
)

# Initialize session state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'transcription_results' not in st.session_state:
    st.session_state.transcription_results = None

# Authentication
if not st.session_state.authenticated:
    st.title("🎙️ Focus Group Transcription Portal")
    st.markdown("### Secure Audio Transcription & Analysis")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.info("📋 This portal provides:\n- Kinyarwanda audio transcription\n- AI-powered text correction\n- Automated summarization\n- English translation")
        
        if st.button("🔐 Login with Google", use_container_width=True):
            if check_authentication():
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("Authentication failed. Please check your credentials.")
    
    st.markdown("---")
    st.caption("Secure • Compliant • AI-Powered")
    st.stop()

# Main App
st.title("🎙️ Kinyarwanda Audio Transcriber")
st.markdown("Upload audio files for transcription, correction, and summarization")

# Sidebar
with st.sidebar:
    st.header("📊 Session Info")
    st.write(f"User: {st.session_state.get('user_email', 'Demo User')}")
    st.write(f"Session: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    
    st.markdown("---")
    st.header("⚙️ Settings")
    chunk_duration = st.slider("Chunk Duration (seconds)", 20, 60, 30)
    
    st.markdown("---")
    if st.button("🚪 Logout"):
        st.session_state.authenticated = False
        st.session_state.transcription_results = None
        st.rerun()

# File upload
audio_file = st.file_uploader(
    "Upload Audio File",
    type=['mp3', 'wav', 'm4a', 'ogg', 'flac'],
    help="Supported formats: MP3, WAV, M4A, OGG, FLAC"
)

if audio_file:
    # Display audio player
    st.audio(audio_file, format=f'audio/{audio_file.name.split(".")[-1]}')
    
    col1, col2 = st.columns([2, 1])
    
    with col2:
        st.metric("File Size", f"{audio_file.size / (1024*1024):.2f} MB")
        st.metric("File Name", audio_file.name)
    
    # Process button
    if st.button("🚀 Start Processing", type="primary", use_container_width=True):
        try:
            # Save uploaded file temporarily
            with tempfile.NamedTemporaryFile(delete=False, suffix=f".{audio_file.name.split('.')[-1]}") as tmp_file:
                tmp_file.write(audio_file.read())
                tmp_path = tmp_file.name
            
            # Progress tracking
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Step 1: Transcription
            status_text.text("🎵 Step 1/3: Transcribing audio...")
            progress_bar.progress(10)
            
            with st.spinner("Loading transcription model..."):
                transcriber = KinyarwandaTranscriber()
                transcriber.load_model()
            
            progress_bar.progress(30)
            status_text.text("🎵 Transcribing audio chunks...")
            
            raw_transcript = transcriber.transcribe_audio(
                tmp_path,
                chunk_duration=chunk_duration,
                save_output=False
            )
            
            progress_bar.progress(50)
            
            # Step 2: Gemini Processing
            status_text.text("🤖 Step 2/3: Processing with Gemini AI...")
            gemini = GeminiProcessor()
            
            cleaned_text = gemini.fix_orthography(raw_transcript)
            progress_bar.progress(70)
            
            summary_rw = gemini.summarize_kinyarwanda(cleaned_text)
            progress_bar.progress(85)
            
            summary_en = gemini.translate_to_english(summary_rw)
            progress_bar.progress(100)
            
            status_text.text("✅ Step 3/3: Complete!")
            
            # Store results
            st.session_state.transcription_results = {
                'raw': raw_transcript,
                'cleaned': cleaned_text,
                'summary_rw': summary_rw,
                'summary_en': summary_en,
                'filename': audio_file.name,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            # Cleanup
            os.unlink(tmp_path)
            
            st.success("✨ Processing complete!")
            st.balloons()
            
        except Exception as e:
            st.error(f"❌ Error during processing: {str(e)}")
            st.exception(e)

# Display results
if st.session_state.transcription_results:
    results = st.session_state.transcription_results
    
    st.markdown("---")
    st.header("📄 Results")
    
    # Tabs for different outputs
    tab1, tab2, tab3, tab4 = st.tabs([
        "📝 Cleaned Transcript",
        "🇷🇼 Summary (Kinyarwanda)",
        "🇬🇧 Summary (English)",
        "🔍 Raw Transcript"
    ])
    
    with tab1:
        st.subheader("Cleaned Transcript with Timestamps")
        st.text_area(
            "Corrected Kinyarwanda Text",
            results['cleaned'],
            height=400,
            key="cleaned_text"
        )
        st.download_button(
            "⬇️ Download Cleaned Transcript",
            results['cleaned'],
            file_name=f"cleaned_transcript_{results['filename']}.txt",
            mime="text/plain"
        )
    
    with tab2:
        st.subheader("Kinyarwanda Summary")
        st.markdown("**Key Insights in Kinyarwanda:**")
        st.text_area(
            "Kinyarwanda Summary",
            results['summary_rw'],
            height=300,
            key="summary_rw"
        )
        st.download_button(
            "⬇️ Download Kinyarwanda Summary",
            results['summary_rw'],
            file_name=f"summary_rw_{results['filename']}.txt",
            mime="text/plain"
        )
    
    with tab3:
        st.subheader("English Summary")
        st.markdown("**Key Insights in English:**")
        st.text_area(
            "English Summary",
            results['summary_en'],
            height=300,
            key="summary_en"
        )
        st.download_button(
            "⬇️ Download English Summary",
            results['summary_en'],
            file_name=f"summary_en_{results['filename']}.txt",
            mime="text/plain"
        )
    
    with tab4:
        st.subheader("Raw Transcription")
        st.caption("Unprocessed output from speech recognition model")
        st.text_area(
            "Raw Transcript",
            results['raw'],
            height=400,
            key="raw_text"
        )
    
    # Export all results
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    
    with col2:
        combined_output = f"""
KINYARWANDA TRANSCRIPTION REPORT
{'='*50}
File: {results['filename']}
Processed: {results['timestamp']}
{'='*50}

CLEANED TRANSCRIPT WITH TIMESTAMPS:
{results['cleaned']}

{'='*50}
SUMMARY (KINYARWANDA):
{results['summary_rw']}

{'='*50}
SUMMARY (ENGLISH):
{results['summary_en']}
"""
        st.download_button(
            "📦 Download Complete Report",
            combined_output,
            file_name=f"complete_report_{results['filename']}.txt",
            mime="text/plain",
            use_container_width=True
        )

# Footer
st.markdown("---")
st.caption("🔒 Secure • AI-Powered Transcription • Focus Group Analysis")
