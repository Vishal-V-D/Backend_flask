# agents/analyzer_agent.py

import google.generativeai as genai

# ✅ Configure Gemini API key (replace with secure method if in production)
genai.configure(api_key="AIzaSyDAG23-f25yrruyGn-GgVcKj46xtJHjQf8")  # Replace this with os.getenv(...) in real deployment

def analyzer_agent(transcript: str) -> str:
    """
    Analyzes the transcript to extract:
    1. Main topics
    2. Speaker tone
    3. Suggested writing style

    Args:
        transcript (str): Raw or cleaned transcript of the podcast/audio.

    Returns:
        str: Analysis result from Gemini as a text block.
    """
    model = genai.GenerativeModel("gemini-2.0-flash")

    prompt = f"""
You are an expert content analyst.

Analyze the following podcast transcript and extract:
1. The main topics discussed
2. The speaker’s tone (e.g., professional, conversational, friendly)
3. A suggested writing style for this audience (e.g., formal, witty, crisp)

Transcript:
\"\"\"
{transcript}
\"\"\"
Return the output as a structured list.
"""

    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"[ERROR] Gemini failed during analysis: {e}"
