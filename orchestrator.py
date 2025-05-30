# agents/orchestrator.py

from transcriber_agent import transcriber_agent
from analyzer_agent import analyzer_agent
from content_agent import content_agent
from seo_agent import seo_agent

def orchestrator(audio_path: str) -> dict:
    """
    Orchestrates the entire MCP pipeline:
    1. Transcribe audio
    2. Analyze transcript
    3. Generate content (blog, LinkedIn post, newsletter)
    4. Generate SEO metadata

    Args:
        audio_path (str): Path to uploaded audio file

    Returns:
        dict: Final structured result
    """
    try:
        # Step 1: Transcription
        transcript = transcriber_agent(audio_path)

        # Step 2: Analyzer agent (tone, style, topics)
        analysis = analyzer_agent(transcript)

        # Step 3: Generate all content sections
        content_output = content_agent(transcript)

        # Parse content sections from raw output
        blog = extract_section(content_output, "BLOG", "LINKEDIN POST")
        linkedin = extract_section(content_output, "LINKEDIN POST", "NEWSLETTER")
        newsletter = extract_section(content_output, "NEWSLETTER", "SEO TITLE")

        # Step 4: SEO from blog only
        seo_raw = seo_agent(blog)
        seo = {
            "title": extract_section(seo_raw, "SEO TITLE", "SEO DESCRIPTION"),
            "description": extract_section(seo_raw, "SEO DESCRIPTION", "SEO KEYWORDS"),
            "keywords": extract_section(seo_raw, "SEO KEYWORDS", None)
        }

        return {
            "transcript": transcript,
            "analysis": analysis,
            "content": {
                "blog": blog,
                "linkedin": linkedin,
                "newsletter": newsletter
            },
            "seo": seo
        }

    except Exception as e:
        return {"error": f"[ERROR in orchestrator] {e}"}


def extract_section(text: str, start_label: str, end_label: str = None) -> str:
    """
    Extracts a section between two labeled headers.
    """
    try:
        start_index = text.upper().index(f"{start_label.upper()}:") + len(start_label) + 1
        end_index = text.upper().index(f"{end_label.upper()}:") if end_label else len(text)
        return text[start_index:end_index].strip()
    except ValueError:
        return ""
