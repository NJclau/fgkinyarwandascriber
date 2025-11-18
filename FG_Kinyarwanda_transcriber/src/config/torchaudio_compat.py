"""
Compatibility shim for torchaudio on CPU-only hosts.

Purpose:
- Provide a safe fallback for missing runtime attributes like list_audio_backends()
  that some torchaudio wheel variations may not expose in minimal/stripped builds.
- Run early (imported before speechbrain/torchaudio usage) to avoid import-time failures.

This file should be safe to import; it intentionally swallows exceptions to avoid
masking real problems during startup.
"""

def _ensure_torchaudio_compat():
    try:
        import torchaudio
    except Exception:
        # If torchaudio import fails entirely, let the downstream code handle it.
        return

    # If older/stripped builds lack list_audio_backends, provide a conservative fallback.
    try:
        if not hasattr(torchaudio, "list_audio_backends"):
            def _fallback_list_audio_backends():
                # return common backend names; speechbrain only queries presence/length in checks
                return ["sox_io", "soundfile"]
            torchaudio.list_audio_backends = _fallback_list_audio_backends
    except Exception:
        # Avoid raising here — leave real failure detection to later imports
        return

# Run shim at import time
_ensure_torchaudio_compat()
