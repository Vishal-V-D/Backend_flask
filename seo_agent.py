# agents/seo_agent.py

import google.generativeai as genai

# ✅ Configure Gemini API key (for development)
genai.configure(api_key="AIzaSyDAG23-f25yrruyGn-GgVcKj46xtJHjQf8")  # Use env variable or Colab secret in production

def seo_agent(blog_text: str) -> str:
    """
    Uses Gemini to generate SEO metadata for a blog post.

    Args:
        blog_text (str): Full blog content.

    Returns:
        str: Text output containing:
            - SEO Title
            - SEO Description
            - SEO Keywords
    """
    model = genai.GenerativeModel("gemini-2.0-flash")

    prompt = f"""
Generate SEO metadata for the following blog content:

Content:
\"\"\"
{blog_text}
\"\"\"

Return clearly labeled results as:
- SEO TITLE:
- SEO DESCRIPTION:
- SEO KEYWORDS:
"""

    try:
        result = model.generate_content(prompt)
        return result.text.strip()
    except Exception as e:
        return f"[ERROR] SEO agent failed: {e}"
