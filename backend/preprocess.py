import re, html
from langdetect import detect

PAT_URL = re.compile(r"https?://\S+")
PAT_MENTION = re.compile(r"@[A-Za-z0-9_]+")
PAT_HASHTAG = re.compile(r"#[A-Za-z0-9_]+")


def _clean(text: str) -> str:
    text = html.unescape(text)
    text = PAT_URL.sub("", text)
    text = PAT_MENTION.sub("", text)
    text = PAT_HASHTAG.sub("", text)
    return text.strip()


def preprocess_texts(texts):
    out = []
    for t in texts:
        t2 = _clean(t)
        # Optionally handle other languages
        try:
            lang = detect(t2)
        except Exception:
            lang = "unknown"
        out.append({"text": t2, "lang": lang})
    return out