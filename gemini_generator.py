# gemini_generator.py

import google.generativeai as genai
import re
from tqdm import tqdm

# ✅ Configure Gemini once globally (tip: use environment variable in production)
genai.configure(api_key="AIzaSyDAG23-f25yrruyGn-GgVcKj46xtJHjQf8")  # Replace securely in Colab, e.g. with os.environ

# -------------------------------
# 🧹 1. Clean transcript text
# -------------------------------
def clean_transcript(text: str) -> str:
    """
    Removes timestamps, filler words, and extra whitespace from transcript.
    """
    text = re.sub(r'\[\d{2}:\d{2}:\d{2}\]', '', text)  # Remove timestamps
    text = re.sub(r'\b(uh|um|you know|like)\b', '', text, flags=re.IGNORECASE)  # Remove filler words
    text = re.sub(r'\s+', ' ', text).strip()  # Normalize whitespace
    return text

# -------------------------------
# ✂️ 2. Chunk transcript into pieces
# -------------------------------
def chunk_text(text: str, max_tokens: int = 2000):
    """
    Yields chunks of text no longer than max_tokens (roughly word-based).
    """
    words = text.split()
    for i in range(0, len(words), max_tokens):
        yield " ".join(words[i:i + max_tokens])

# -------------------------------
# 📄 3. Summarize chunks using Gemini
# -------------------------------
def summarize_chunks(chunks, model) -> str:
    """
    Uses Gemini to summarize each chunk and return one unified summary.
    """
    summaries = []
    print("🔄 Summarizing transcript chunks...")
    for chunk in tqdm(chunks):
        response = model.generate_content(f"Summarize this part of a transcript:\n\n{chunk}")
        summaries.append(response.text.strip())
    return "\n".join(summaries)

# -------------------------------
# 📝 4. Generate content from summary
# -------------------------------
def generate_final_outputs(summary: str, model) -> str:
    """
    Prompts Gemini to return blog, LinkedIn post, newsletter, and SEO metadata.
    """
    prompt = f"""
Transcript Summary:
{summary}

Tasks:
use the above transcript provided to :
1. Generate a SEO-optimized blog post with a heading and other suitable components-matching near to close professional blog..
2. Write a professional LinkedIn post, with emojies for easy read, #tags and to topics based content gathering the right audience.dont give paragraphs.
3. Draft a short newsletter for email, with crisp user holding sentences to capture their attention through-out their entire reading period.
4. Generate SEO metadata with title, description, and comma-separated keywords matching with the latest trends .

Return response clearly labeled with:
- BLOG:
- LINKEDIN POST:
- NEWSLETTER:
- SEO TITLE:
- SEO DESCRIPTION:
- SEO KEYWORDS:
"""
    response = model.generate_content(prompt)
    return response.text.strip()

# -------------------------------
# 🎯 5. Main wrapper (used only in trial version)
# -------------------------------
def generate_content(transcription: str) -> str:
    """
    Full pipeline to generate all content from raw transcript.
    (Still useful for standalone testing or debugging)
    """
    model = genai.GenerativeModel("gemini-2.0-flash")

    cleaned = clean_transcript(transcription)
    chunks = list(chunk_text(cleaned, max_tokens=2000))
    summary = summarize_chunks(chunks, model)
    return generate_final_outputs(summary, model)
