import os
import tempfile
from faster_whisper import WhisperModel
from pydub import AudioSegment
import librosa
import soundfile as sf

class KinyarwandaTranscriber:

    def __init__(self):
        # Load HF model in CPU mode, int8 for faster Streamlit inference
        self.model = WhisperModel(
            "leophill/whisper-large-v3-sn-kinyarwanda-ct2",
            device="cpu",
            compute_type="int8"
        )

        self.decode_options = dict(
            language="rw",
            beam_size=5,
            best_of=5,
            vad_filter=True,
            vad_parameters={"min_silence_duration_ms": 500},
            word_timestamps=False
        )

    def preprocess_audio(self, uploaded_file):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            audio = AudioSegment.from_file(uploaded_file)
            audio = audio.set_channels(1).set_frame_rate(16000)
            audio.export(tmp.name, format="wav")
            return tmp.name

    def transcribe(self, uploaded_audio_file):
        wav_path = self.preprocess_audio(uploaded_audio_file)
        segments, info = self.model.transcribe(wav_path, **self.decode_options)

        transcript = " ".join([seg.text for seg in segments])
        return transcript.strip()
