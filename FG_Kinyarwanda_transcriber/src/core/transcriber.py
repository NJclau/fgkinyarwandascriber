import os
import gc
import librosa
from pydub import AudioSegment
from speechbrain.inference.ASR import EncoderASR
import streamlit as st
from src.config.settings import config

class KinyarwandaTranscriber:
    """A class for transcribing Kinyarwanda audio using a SpeechBrain model.

    Attributes:
        model: The SpeechBrain ASR model.
        model_loaded: A boolean indicating whether the model has been loaded.
    """

    def __init__(self):
        """Initializes the KinyarwandaTranscriber."""
        self.model = None
        self.model_loaded = False
        print("Kinyarwanda Transcriber initialized")

    def load_model(self):
        """Loads the SpeechBrain ASR model.

        Raises:
            Exception: If the model fails to load.
        """
        print("Loading SpeechBrain Kinyarwanda ASR model...")

        try:
            # Load model with GPU support if available
            run_opts = {"device": "cuda"} if config.use_gpu else {"device": "cpu"}

            self.model = EncoderASR.from_hparams(
                source="speechbrain/asr-wav2vec2-commonvoice-14-rw",
                savedir="pretrained_models/asr-wav2vec2-commonvoice-14-rw",
                run_opts=run_opts,
            )
            self.model_loaded = True
            print("✓ Model loaded successfully")

        except Exception as e:
            raise Exception(f"Failed to load model: {str(e)}")

    def preprocess_audio(self, input_path, target_sr=16000):
        """Converts audio to the required format (mono, 16kHz WAV).

        Args:
            input_path: The path to the input audio file.
            target_sr: The target sample rate.

        Returns:
            The path to the processed audio file.
        """
        try:
            audio = AudioSegment.from_file(input_path)
            audio = audio.set_channels(1).set_frame_rate(target_sr)
            
            temp_path = "/tmp/processed_audio.wav"
            audio.export(temp_path, format="wav")
            return temp_path
        except Exception as e:
            print(f"Error processing audio: {e}")
            raise

    def chunk_audio(self, audio_path, chunk_duration=30):
        """Splits an audio file into chunks with timestamps.

        Args:
            audio_path: The path to the audio file.
            chunk_duration: The duration of each chunk in seconds.

        Returns:
            A tuple containing a list of chunk file paths, a list of timestamps,
            and the total duration of the audio.
        """
        audio, sr = librosa.load(audio_path, sr=16000, mono=True)
        duration = len(audio) / sr

        chunks = []
        timestamps = []

        chunk_samples = int(chunk_duration * sr)
        overlap_samples = int(2 * sr)  # 2-second overlap

        start = 0
        while start < len(audio):
            end = min(start + chunk_samples, len(audio))
            chunk = audio[start:end]

            if len(chunk) > sr:  # Only process chunks > 1 second
                chunk_path = f"/tmp/chunk_{len(chunks)}.wav"
                librosa.output.write_wav(chunk_path, chunk, sr)
                chunks.append(chunk_path)
                timestamps.append((start / sr, end / sr))

            start = end - overlap_samples
            if start >= len(audio) - overlap_samples:
                break

        return chunks, timestamps, duration

    def transcribe_chunk(self, chunk_path):
        """Transcribes a single audio chunk.

        Args:
            chunk_path: The path to the audio chunk.

        Returns:
            The transcription of the audio chunk.
        """
        if not self.model_loaded:
            raise ValueError("Model not loaded! Call load_model() first.")

        try:
            transcription = self.model.transcribe_file(chunk_path)
            return transcription.strip()
        except Exception as e:
            print(f"Error transcribing chunk: {e}")
            return "[TRANSCRIPTION_ERROR]"

    def transcribe_audio(self, audio_path, chunk_duration=30, save_output=False):
        """Transcribes an audio file with progress tracking.

        Args:
            audio_path: The path to the audio file.
            chunk_duration: The duration of each chunk in seconds.
            save_output: A boolean indicating whether to save the output to a file.

        Returns:
            The full transcription of the audio file.
        """
        if not self.model_loaded:
            self.load_model()

        print(f"Processing: {audio_path}")
        
        # Preprocess
        processed_path = self.preprocess_audio(audio_path)
        
        # Split into chunks
        chunks, timestamps, total_duration = self.chunk_audio(processed_path, chunk_duration)
        print(f"Audio duration: {total_duration:.1f}s ({len(chunks)} chunks)")
        
        # Progress tracking
        progress_container = None
        try:
            progress_container = st.progress(0)
        except:
            pass
        
        # Transcribe chunks
        full_transcription = []
        for i, (chunk_path, (start_t, end_t)) in enumerate(zip(chunks, timestamps)):
            print(f"Chunk {i+1}/{len(chunks)} ({start_t:.1f}s - {end_t:.1f}s)")
            
            transcription = self.transcribe_chunk(chunk_path)
            timestamp = f"[{self._format_time(start_t)} - {self._format_time(end_t)}]"
            full_transcription.append(f"{timestamp}\n{transcription}")
            
            # Update progress
            if progress_container:
                progress_container.progress((i + 1) / len(chunks))
            
            # Cleanup chunk file
            if os.path.exists(chunk_path):
                os.remove(chunk_path)
            
            # Memory cleanup
            if i % 10 == 0:
                gc.collect()
        
        # Cleanup
        if os.path.exists(processed_path):
            os.remove(processed_path)
        
        final_transcription = "\n\n".join(full_transcription)
        
        if save_output:
            with open("kinyarwanda_transcription.txt", "w", encoding="utf-8") as f:
                f.write(final_transcription)
            print("✓ Saved to kinyarwanda_transcription.txt")
        
        return final_transcription

    def _format_time(self, seconds):
        """Formats seconds to the HH:MM:SS format.

        Args:
            seconds: The number of seconds to format.

        Returns:
            A string representing the time in HH:MM:SS format.
        """
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
