# agents/content_agent.py

from gemini_generator import (
    clean_transcript,
    chunk_text,
    summarize_chunks,
    generate_final_outputs
)
import google.generativeai as genai

# ✅ Configure Gemini API key (replace securely in production)
genai.configure(api_key="AIzaSyDAG23-f25yrruyGn-GgVcKj46xtJHjQf8")

def content_agent(transcript: str) -> str:
    """
    Agent to generate final blog, LinkedIn post, and newsletter using Gemini,
    based on the summarized podcast transcript.

    Args:
        transcript (str): Raw or cleaned transcript of the audio.

    Returns:
        str: Combined content with labeled sections (BLOG, LINKEDIN POST, etc.)
    """
    try:
        model = genai.GenerativeModel("gemini-2.0-flash")

        # Step 1: Clean the raw transcript
        cleaned = clean_transcript(transcript)

        # Step 2: Break transcript into manageable chunks
        chunks = list(chunk_text(cleaned, max_tokens=2000))

        # Step 3: Summarize chunks
        summary = summarize_chunks(chunks, model)

        # Step 4: Generate structured outputs (Blog, LinkedIn, Newsletter, etc.)
        return generate_final_outputs(summary, model)

    except Exception as e:
        return f"[ERROR] Content agent failed: {e}"
