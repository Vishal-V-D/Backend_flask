# agents/final_content_agent.py

import google.generativeai as genai
genai.configure(api_key="AIzaSyDAG23-f25yrruyGn-GgVcKj46xtJHjQf8")

def final_content_agent(transcript: str, raw: str, content_type="blog") -> str:
    """
    Generates the final content by:
    - Validating factual alignment with transcript
    - Enriching the language and structure
    - Improving formatting for the intended platform
    """
    model = genai.GenerativeModel("gemini-2.0-flash")

    prompt = f"""
Improve the following {content_type} to ensure it is:
1. Factually aligned with the transcript
2. Enriched with engaging, clear, concise language
3. Formatted perfectly for its platform

Transcript:
\"\"\"
{transcript}
\"\"\"

Original {content_type.capitalize()}:
\"\"\"
{raw}
\"\"\"

Instructions:
- Use examples and analogies only if found in the transcript
- Don’t invent facts or fake data
- Format well (headings, emojis, #hashtags, subject lines where needed)
- Return only the improved {content_type}
"""

    try:
        result = model.generate_content(prompt)
        return result.text.strip()
    except Exception as e:
        return f"[ERROR] Final content generation failed: {e}"
