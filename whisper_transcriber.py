# whisper_transcriber.py

from pydub import AudioSegment
from tqdm import tqdm
import tempfile
from faster_whisper import WhisperModel

# ✅ Load faster-whisper model (configurable)
MODEL_SIZE = "tiny"  # Options: "tiny", "base", "small", "medium", "large"
model = WhisperModel(MODEL_SIZE, compute_type="int8", cpu_threads=4)

def transcribe_audio(audio_path, chunk_length_ms=60000):
    """
    Transcribes an audio file using Faster-Whisper with chunking and temp file I/O.
    
    Args:
        audio_path (str): Path to the input audio file.
        chunk_length_ms (int): Length of audio chunks in milliseconds.
        
    Returns:
        str: Full transcribed text.
    """
    audio = AudioSegment.from_file(audio_path)
    duration_ms = len(audio)

    full_transcript = ""
    num_chunks = (duration_ms // chunk_length_ms) + 1

    print(f"🔍 Transcribing {duration_ms / 60000:.1f} minutes of audio in {num_chunks} chunks...\n")

    for i, start_ms in enumerate(tqdm(range(0, duration_ms, chunk_length_ms))):
        end_ms = min(start_ms + chunk_length_ms, duration_ms)
        chunk = audio[start_ms:end_ms]

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=True) as temp_wav:
            chunk.export(temp_wav.name, format="wav")

            segments, _ = model.transcribe(temp_wav.name, beam_size=1)
            chunk_text = " ".join([seg.text for seg in segments]).strip()

            print(f"\n[Chunk {i + 1}]:\n{chunk_text}\n")
            full_transcript += chunk_text + " "

    return full_transcript.strip()
