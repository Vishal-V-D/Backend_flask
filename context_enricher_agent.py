# agents/context_enricher_agent.py

import google.generativeai as genai
genai.configure(api_key="AIzaSyDAG23-f25yrruyGn-GgVcKj46xtJHjQf8")

def context_enricher_agent(topics: list[str]) -> str:
    """
    Uses Gemini to suggest trending or authoritative external links.

    Args:
        topics (list of str): List of core topics (from analyzer).

    Returns:
        str: Suggested links in Markdown format.
    """
    model = genai.GenerativeModel("gemini-2.0-flash")
    topic_string = ", ".join(topics)

    prompt = f"""
Suggest 3 high-quality, trending, or helpful links related to the following topics:
{topic_string}

Return them as Markdown list:
1. [Title](URL)
2. ...
3. ...
"""
    try:
        result = model.generate_content(prompt)
        return result.text.strip()
    except Exception as e:
        return f"[ERROR] Enricher agent failed: {e}"
