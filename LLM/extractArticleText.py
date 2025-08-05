import openai
from typing import Optional

def extract_press_release_body(markdown: str,
                               api_key: str,
                               model: str = "gpt-4o-mini-2024-07-18") -> str:
    """
    Given the full markdown of a DOJ press release, return only the main
    announcement text—i.e., the narrative body—stripped of all markdown,
    headings, lists, footers, Contact blocks, and boilerplate.
    """
    client = openai.OpenAI(api_key=api_key)
    prompt = f"""
You’re given the full markdown of a DOJ press release. Your job is to return
only the main announcement text—the narrative paragraphs that make up the body
of the release—stripped of all markdown, headings (including the opening
dateline), lists, tables, footers, “Contact” blocks, and any boilerplate.

Output plain, unformatted text of the announcement only.

Markdown:
{markdown}
"""
    resp = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You output exactly the announcement text."},
            {"role": "user",   "content": prompt}
        ],
        temperature=0.0
    )
    return resp.choices[0].message.content.strip()
