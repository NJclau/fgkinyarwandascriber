import streamlit as st
import os
import tempfile
from datetime import datetime
from src.core.transcriber import KinyarwandaTranscriber
from src.core.gemini_processor import GeminiProcessor
from src.services.admin_handler import UserManager, AdminDashboard
from src.services.pipeline import TranscriptionPipeline
from src.config.settings import config

# Page config
st.set_page_config(
    page_title="Kinyarwanda Focus Group Transcriber",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'user_email' not in st.session_state:
    st.session_state.user_email = None
if 'page' not in st.session_state:
    st.session_state.page = 'home'
if 'transcription_results' not in st.session_state:
    st.session_state.transcription_results = None
if 'streaming' not in st.session_state:
    st.session_state.streaming = False
if 'transcription_generator' not in st.session_state:
    st.session_state.transcription_generator = None

# Initialize managers
user_manager = UserManager()
admin_dashboard = AdminDashboard()

# Inject config into user_manager
user_manager.admin_emails = config.admin_emails


def render_login_page():
    """Renders the login and access request page."""
    st.title("🎙️ Kinyarwanda Focus Group Transcriber")
    st.markdown("### Secure Audio Transcription & Analysis Portal")

    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.info("""
        **Features:**
        - 🎯 Kinyarwanda audio transcription
        - ✨ AI-powered text correction
        - 📝 Automated summarization
        - 🌍 English translation
        - 🔒 Secure access control
        """)
        
        tab1, tab2 = st.tabs(["🔐 Login", "📝 Request Access"])
        
        with tab1:
            st.markdown("#### Login with Approved Email")
            email = st.text_input("Email Address", key="login_email")
            
            if st.button("🔓 Login", use_container_width=True):
                email = email.strip().lower()
                
                if user_manager.is_admin(email):
                    st.session_state.authenticated = True
                    st.session_state.user_email = email
                    st.session_state.is_admin = True
                    st.success("✅ Admin login successful!")
                    st.rerun()
                
                elif user_manager.is_approved_user(email):
                    st.session_state.authenticated = True
                    st.session_state.user_email = email
                    st.session_state.is_admin = False
                    st.success("✅ Login successful!")
                    st.rerun()
                
                else:
                    st.error("❌ Access denied. Request access or contact admin.")
        
        with tab2:
            st.markdown("#### Request Portal Access")
            
            with st.form("access_request_form"):
                req_email = st.text_input("Email Address*")
                req_name = st.text_input("Full Name*")
                req_org = st.text_input("Organization*")
                req_reason = st.text_area("Reason for Access*", 
                    placeholder="Explain how you will use this tool...")
                
                submitted = st.form_submit_button("📤 Submit Request", use_container_width=True)
                
                if submitted:
                    if not all([req_email, req_name, req_org, req_reason]):
                        st.error("⚠️ All fields are required")
                    else:
                        req_email = req_email.strip().lower()
                        
                        if user_manager.request_access(req_email, req_name, req_org, req_reason):
                            st.success("""
                            ✅ **Access request submitted!**
                            
                            Your request will be reviewed by an administrator.
                            You will receive notification once approved.
                            """)
                        else:
                            st.warning("⚠️ You already have a pending request or active account")
    
    st.markdown("---")
    st.caption("🔒 Secure • 🤖 AI-Powered • 📊 Focus Group Analysis")


def render_transcription_page():
    """Renders the main transcription page."""
    st.title("🎙️ Audio Transcription & Analysis")

    # Sidebar
    with st.sidebar:
        st.header("📊 Session Info")
        st.write(f"👤 **User:** {st.session_state.user_email}")
        st.write(f"🕐 **Time:** {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        
        if st.session_state.get('is_admin', False):
            st.success("🔑 Admin Account")
        
        st.markdown("---")
        st.header("⚙️ Processing Settings")
        chunk_duration = st.slider("Chunk Duration (sec)", 20, 60, 30)
        
        st.markdown("---")
        
        # Navigation
        if st.session_state.get('is_admin', False):
            if st.button("🔐 Admin Dashboard", use_container_width=True):
                st.session_state.page = 'admin'
                st.rerun()
        
        if st.button("🔓 Logout", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.user_email = None
            st.session_state.page = 'home'
            st.session_state.transcription_results = None
            st.rerun()
    
    # Mode switcher
    is_streaming_mode = st.toggle("Streaming Mode", key="streaming_mode_toggle")

    if is_streaming_mode:
        st.markdown("### 🔴 Streaming Transcription")

        # UI for streaming
        if st.session_state.streaming:
            if st.button("⏹️ Stop Streaming", use_container_width=True):
                st.session_state.streaming = False
                st.session_state.transcription_generator = None
                st.rerun()

        st.markdown("---")
        placeholder = st.empty()
        placeholder = st.empty()
        
        # Displaying the transcription
        if st.session_state.get('streaming', False) and st.session_state.get('transcription_generator'):
            full_transcript = ""
            placeholder.markdown("### 🔴 Live Transcription")
            transcript_area = st.empty()

            # Update UI with new segments
            for segment in st.session_state.transcription_generator:
                full_transcript += segment
                transcript_area.text_area("Transcript", full_transcript, height=300)

            st.session_state.streaming = False
            st.session_state.transcription_generator = None
            st.success("Streaming finished!")
        else:
            placeholder.info("Upload an audio file to start streaming.")

        # Audio uploader for streaming
        uploaded_audio = st.file_uploader(
            "Upload an audio file to start streaming",
            type=['mp3', 'wav', 'm4a', 'ogg', 'flac'],
            key="streaming_uploader"
        )

        if uploaded_audio and not st.session_state.get('streaming', False):
            # Save the uploaded file to a temporary path
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio_file:
                temp_audio_file.write(uploaded_audio.getvalue())
                temp_audio_path = temp_audio_file.name

            # Start the transcription and store the generator
            st.session_state.streaming = True
            st.session_state.transcription_generator = stream_transcription(
                temp_audio_path, chunk_duration
            )
            st.rerun()

    else:
        # File upload
        st.markdown("### 📁 Upload Audio File")
        audio_file = st.file_uploader(
            "Select audio file for transcription",
            type=['mp3', 'wav', 'm4a', 'ogg', 'flac'],
            help="Supported: MP3, WAV, M4A, OGG, FLAC (Max 50MB)"
        )
        
        if audio_file:
            col1, col2, col3 = st.columns([2, 1, 1])

            with col1:
                st.audio(audio_file, format=f'audio/{audio_file.name.split(".")[-1]}')

            with col2:
                st.metric("📦 File Size", f"{audio_file.size / (1024*1024):.2f} MB")

            with col3:
                st.metric("📄 File Name", audio_file.name)

            # Process button
            if st.button("🚀 Start Processing", type="primary", use_container_width=True):
                process_audio(audio_file, chunk_duration)


def _format_time(seconds):
    """Formats seconds to the HH:MM:SS format."""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"


def stream_transcription(audio_path, chunk_duration):
    """
    A generator that transcribes an audio file in chunks and yields results.
    This function re-implements the transcription logic from the
    KinyarwandaTranscriber class to allow for real-time streaming output
    without modifying the core class.

    Args:
        audio_path (str): Path to the audio file.
        chunk_duration (int): Duration of each chunk in seconds.

    Yields:
        str: Formatted transcription segments.
    """
    transcriber = KinyarwandaTranscriber()
    processed_path = None
    chunks = []

    try:
        if not transcriber.model_loaded:
            with st.spinner("Loading transcription model..."):
                transcriber.load_model()
        
        # Process and chunk audio using methods from the transcriber class
        processed_path = transcriber.preprocess_audio(audio_path)
        chunks, timestamps, total_duration = transcriber.chunk_audio(
            processed_path, chunk_duration
        )
        
        st.info(f"Audio ready for streaming ({len(chunks)} chunks)...")

        # Transcribe each chunk and yield the result
        for i, (chunk_path, (start_t, end_t)) in enumerate(zip(chunks, timestamps)):
            # Check if user has stopped the streaming
            if not st.session_state.get('streaming', False):
                yield "\n[STREAMING STOPPED BY USER]"
                break

            transcription = transcriber.transcribe_chunk(chunk_path)
            timestamp = f"[{_format_time(start_t)} - {_format_time(end_t)}]"
            segment = f"{timestamp}\n{transcription}\n\n"
            yield segment

    except Exception as e:
        st.error(f"Error during streaming transcription: {e}")
        yield "\n[TRANSCRIPTION ERROR]"
    finally:
        # Cleanup all temporary files
        if processed_path and os.path.exists(processed_path):
            os.remove(processed_path)
        for chunk_path in chunks:
            if os.path.exists(chunk_path):
                os.remove(chunk_path)


def process_audio(audio_file, chunk_duration):
    """Processes an audio file through the transcription pipeline.

    Args:
        audio_file: The audio file to process.
        chunk_duration: The duration of each chunk in seconds.
    """
    try:
        # Save uploaded file
        with tempfile.NamedTemporaryFile(
            delete=False, suffix=f".{audio_file.name.split('.')[-1]}"
        ) as tmp_file:
            tmp_file.write(audio_file.read())
            tmp_path = tmp_file.name
        
        pipeline = TranscriptionPipeline()
        results = pipeline.run(tmp_path, chunk_duration)
        
        # Store results
        st.session_state.transcription_results = {
            **results,
            'filename': audio_file.name,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # Log usage
        file_size_mb = audio_file.size / (1024*1024)
        duration_sec = 0  # Calculate from audio if needed
        admin_dashboard.log_usage(
            st.session_state.user_email,
            audio_file.name,
            file_size_mb,
            duration_sec
        )
        
        # Cleanup
        os.unlink(tmp_path)
        
        st.success("✨ Processing complete!")
        st.balloons()
        
        # Display results
        display_results()
        
    except Exception as e:
        st.error(f"❌ Error during processing: {str(e)}")
        st.exception(e)


def display_results():
    """Displays the transcription results."""
    if not st.session_state.transcription_results:
        return

    results = st.session_state.transcription_results
    
    st.markdown("---")
    st.header("📊 Results")
    
    tab1, tab2, tab3, tab4 = st.tabs([
        "✨ Cleaned Transcript",
        "📝 Summary (Kinyarwanda)",
        "🌍 Summary (English)",
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
            mime="text/plain",
            use_container_width=True
        )
    
    with tab2:
        st.subheader("Kinyarwanda Summary")
        st.text_area(
            "Summary in Kinyarwanda",
            results['summary_rw'],
            height=300,
            key="summary_rw"
        )
        st.download_button(
            "⬇️ Download Kinyarwanda Summary",
            results['summary_rw'],
            file_name=f"summary_rw_{results['filename']}.txt",
            mime="text/plain",
            use_container_width=True
        )
    
    with tab3:
        st.subheader("English Summary")
        st.text_area(
            "Summary in English",
            results['summary_en'],
            height=300,
            key="summary_en"
        )
        st.download_button(
            "⬇️ Download English Summary",
            results['summary_en'],
            file_name=f"summary_en_{results['filename']}.txt",
            mime="text/plain",
            use_container_width=True
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
    
    # Complete report export
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col2:
        combined_output = f"""
KINYARWANDA TRANSCRIPTION REPORT
{'='*60}
File: {results['filename']}
Processed: {results['timestamp']}
User: {st.session_state.user_email}
{'='*60}

CLEANED TRANSCRIPT WITH TIMESTAMPS:
{results['cleaned']}

{'='*60}
SUMMARY (KINYARWANDA):
{results['summary_rw']}

{'='*60}
SUMMARY (ENGLISH):
{results['summary_en']}

{'='*60}
Generated by: Kinyarwanda Focus Group Transcriber
        """
        
        st.download_button(
            "📄 Download Complete Report",
            combined_output,
            file_name=f"complete_report_{results['filename']}.txt",
            mime="text/plain",
            use_container_width=True
        )


# Main app routing
if not st.session_state.authenticated:
    render_login_page()

elif st.session_state.page == 'admin' and st.session_state.get('is_admin', False):
    admin_dashboard.render(st.session_state.user_email)
    
    # Back button
    if st.sidebar.button("⬅️ Back to Transcription", use_container_width=True):
        st.session_state.page = 'home'
        st.rerun()

else:
    render_transcription_page()

# Footer
st.markdown("---")
st.caption("🔒 Secure • 🤖 AI-Powered • 📊 Focus Group Analysis • Built by DinoSoft")
