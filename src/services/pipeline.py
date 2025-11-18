import streamlit as st
from src.core.transcriber import KinyarwandaTranscriber
from src.core.gemini_processor import GeminiProcessor

class TranscriptionPipeline:
  """Complete transcription pipeline orchestrator"""

  def __init__(self):
    self.transcriber = None
    self.gemini = None

  @st.cache_resource
  def _get_transcriber(_self):
    """Load and cache transcriber"""
    transcriber = KinyarwandaTranscriber()
    transcriber.load_model()
    return transcriber

  @st.cache_resource
  def _get_gemini(_self):
    """Load and cache Gemini processor"""
    return GeminiProcessor()

  def run(self, audio_path: str, chunk_duration: int = 30) -> dict:
    """Run complete transcription pipeline

    Args:
      audio_path: Path to audio file
      chunk_duration: Duration of audio chunks in seconds

    Returns:
      dict with keys: raw, cleaned, summary_rw, summary_en
    """
    try:
      # Initialize components
      if not self.transcriber:
        self.transcriber = self._get_transcriber()
      if not self.gemini:
        self.gemini = self._get_gemini()

      # Step 1: Transcribe audio
      st.info("🎙️ Transcribing audio...")
      raw_transcript = self.transcriber.transcribe_audio(
        audio_path,
        chunk_duration=chunk_duration,
        save_output=False
      )

      # Step 2: Fix orthography
      st.info("✨ Correcting orthography and grammar...")
      cleaned_transcript = self.gemini.fix_orthography(raw_transcript)

      # Step 3: Summarize in Kinyarwanda
      st.info("📝 Generating Kinyarwanda summary...")
      summary_rw = self.gemini.summarize_kinyarwanda(cleaned_transcript)

      # Step 4: Translate to English
      st.info("🌍 Translating to English...")
      summary_en = self.gemini.translate_to_english(summary_rw)

      return {
        'raw': raw_transcript,
        'cleaned': cleaned_transcript,
        'summary_rw': summary_rw,
        'summary_en': summary_en,
        'status': 'success'
      }

    except Exception as e:
      st.error(f"Pipeline error: {str(e)}")
      return {
        'status': 'error',
        'error': str(e)
      }