# agents/transcriber_agent.py

from whisper_transcriber import transcribe_audio

def transcriber_agent(audio_path: str) -> str:
    """
    Agent to handle audio transcription using Faster-Whisper.

    Args:
        audio_path (str): Path to the uploaded audio file.

    Returns:
        str: Full transcript as a single string.
    """
    try:
        transcript = transcribe_audio(audio_path)
        return transcript
    except Exception as e:
        return f"[ERROR] Transcription failed: {e}"
