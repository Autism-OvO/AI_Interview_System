import os
from typing import Optional


# Cache local whisper model in-process to avoid reloading on each request.
_WHISPER_MODEL_CACHE = None
_WHISPER_MODEL_NAME = None

# Ensure ffmpeg from static_ffmpeg is on PATH if system ffmpeg is missing
try:
    import shutil
    if not shutil.which("ffmpeg"):
        try:
            import static_ffmpeg
            _ffmpeg, _ = static_ffmpeg.run.get_or_fetch_platform_executables_else_raise()
            os.environ["PATH"] = os.path.dirname(_ffmpeg) + os.pathsep + os.environ.get("PATH", "")
        except Exception:
            pass
except Exception:
    pass


def _get_openai_api_key() -> Optional[str]:
    """Return OpenAI API key from env or key.py."""
    k = os.getenv("OPENAI_API_KEY")
    if k:
        return k
    try:
        from key import key as _keys
        return _keys.get('gpt', '')
    except Exception:
        return None


def _get_cached_whisper_model(model_name: str):
    """Load whisper model once and reuse it for subsequent requests."""
    global _WHISPER_MODEL_CACHE, _WHISPER_MODEL_NAME
    if _WHISPER_MODEL_CACHE is not None and _WHISPER_MODEL_NAME == model_name:
        return _WHISPER_MODEL_CACHE

    import whisper
    _WHISPER_MODEL_CACHE = whisper.load_model(model_name)
    _WHISPER_MODEL_NAME = model_name
    return _WHISPER_MODEL_CACHE


def transcribe_file(filepath: str) -> str:
    """Try to transcribe audio file using local whisper if available.

    Returns transcribed text or raises RuntimeError with instructions.
    """
    # prefer whisper package (local models)
    try:
        import whisper
    except Exception:
        whisper = None

    if whisper is not None and hasattr(whisper, "load_model"):
        model_name = os.getenv("WHISPER_MODEL", "small")
        try:
            model = _get_cached_whisper_model(model_name)
            res = model.transcribe(filepath)
            return res.get("text", "").strip()
        except Exception as e:
            print(f"Local whisper failed, trying fallback: {e}")
            # Do not raise here; allow fallback to OpenAI API

    # fallback: if OPENAI_API_KEY exists, user can use OpenAI's Whisper API
    api_key = _get_openai_api_key()
    if api_key:
        try:
            import openai
        except Exception:
            raise RuntimeError("openai package not installed for remote transcription")

        # Support new and old openai SDKs
        try:
            if hasattr(openai, "OpenAI"):
                timeout_s = float(os.getenv("OPENAI_TRANSCRIBE_TIMEOUT", "120"))
                client = openai.OpenAI(api_key=api_key, timeout=timeout_s)
                # new SDK: client.audio.transcriptions.create
                try:
                    with open(filepath, "rb") as f:
                        resp = client.audio.transcriptions.create(model="whisper-1", file=f)
                        # try to extract text
                        text = None
                        try:
                            text = resp.text
                        except Exception:
                            try:
                                text = resp.get('text')
                            except Exception:
                                text = str(resp)
                        return (text or "").strip()
                except Exception as e:
                    raise RuntimeError(f"OpenAI transcription (new SDK) failed: {e}")
            else:
                openai.api_key = api_key
                try:
                    with open(filepath, "rb") as f:
                        # older patterns
                        if hasattr(openai, 'Audio') and hasattr(openai.Audio, 'transcribe'):
                            resp = openai.Audio.transcribe("whisper-1", f)
                            return resp.get("text", "").strip()
                        else:
                            resp = openai.Transcription.create(file=f, model="whisper-1")
                            return resp.get("text", "").strip()
                except Exception as e:
                    raise RuntimeError(f"OpenAI transcription (old SDK) failed: {e}")
        except Exception as e:
            raise

    raise RuntimeError("No transcription backend available. Install 'whisper' and 'ffmpeg', or set OPENAI_API_KEY and use OpenAI transcription.")
