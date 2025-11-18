# src/services/pipeline.py

from src.core.transcriber import KinyarwandaTranscriber
from src.core.gemini_processor import GeminiProcessor

class TranscriptionPipeline:
    def __init__(self):
        self.transcriber = KinyarwandaTranscriber()
        self.gemini_processor = GeminiProcessor()

    def run(self, audio_file_path: str, chunk_duration: int = 30):
        # Step 1: Transcribe the audio file
        raw_transcript = self.transcriber.transcribe_audio(
            audio_file_path,
            chunk_duration=chunk_duration,
            save_output=False
        )

        # Step 2: Process the transcript with Gemini
        processed_data = self.gemini_processor.process_full_pipeline(raw_transcript)

        return {
            'raw': raw_transcript,
            **processed_data
        }
