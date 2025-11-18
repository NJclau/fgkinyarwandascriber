"""
Compatibility shim for torchaudio on CPU-only hosts.

Purpose:
- Provide a fallback for missing runtime attributes like list_audio_backends()
  that some torchaudio wheel variations may not expose in minimal/stripped builds.
- Run early (imported before speechbrain/torchaudio usage) to avoid import-time failures.

This shim is intentionally conservative: it does not emulate torchaudio decoding,
it only supplies missing attributes used by SpeechBrain during import checks.
"""

def _ensure_torchaudio_compat():
    try:
        import torchaudio
    except Exception:
        # torchaudio not importable — let downstream code handle the error
        return

    try:
        # Provide a safe fallback for list_audio_backends if absent
        if not hasattr(torchaudio, "list_audio_backends"):
            def _fallback_list_audio_backends():
                # Return plausible backends; SpeechBrain only checks for presence/length
                return ["sox_io", "soundfile"]
            torchaudio.list_audio_backends = _fallback_list_audio_backends

        # Provide a no-op for set_audio_backend if absent (some versions use it)
        if not hasattr(torchaudio, "set_audio_backend"):
            def _noop_set_audio_backend(name):
                return None
            torchaudio.set_audio_backend = _noop_set_audio_backend

    except Exception:
        # Never raise on compatibility shim — leave real errors to real imports
        return

# Execute the shim at import time
_ensure_torchaudio_compat()
