import os
import sys
import json
import datetime as dt
import urllib.request
import urllib.error
from zoneinfo import ZoneInfo

TIMEZONE = "Europe/Istanbul"
DISCLAIMER = "⚠️ تنبيه: هذا منشور معلوماتي عام وليس استشارة قانونية."

def load_posts(path="posts.json"):
    with open(path, "r", encoding="utf-8") as f:
        posts = json.load(f)
    if not isinstance(posts, list) or not posts:
        raise ValueError("posts.json يجب أن يحتوي على قائمة منشورات غير فارغة.")
    return posts

def build_message(post):
    if isinstance(post, str):
        return f"{post.strip()}\n\n{DISCLAIMER}"

    title = post.get("title", "").strip()
    body = post.get("body", "").strip()
    question = post.get("question", "").strip()
    hashtags = post.get("hashtags", "").strip()

    parts = []
    if title:
        parts.append(title)
    if body:
        parts.append(body)
    if question:
        parts.append(question)
    parts.append(DISCLAIMER)
    if hashtags:
        parts.append(hashtags)

    return "\n\n".join(parts).strip()

def choose_daily_post(posts):
    today = dt.datetime.now(ZoneInfo(TIMEZONE)).date()
    start = dt.date(2026, 1, 1)
    index = (today.toordinal() - start.toordinal()) % len(posts)
    return posts[index], today.isoformat(), index

def send_telegram_message(token, chat_id, text):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = json.dumps({
        "chat_id": chat_id,
        "text": text,
        "disable_web_page_preview": True
    }).encode("utf-8")

    req = urllib.request.Request(
        url,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST"
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            response_body = resp.read().decode("utf-8")
            print("Telegram response:", response_body)
    except urllib.error.HTTPError as e:
        print("Telegram HTTP error:", e.code, e.read().decode("utf-8"), file=sys.stderr)
        raise
    except Exception as e:
        print("Telegram error:", str(e), file=sys.stderr)
        raise

def main():
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")

    if not token:
        raise RuntimeError("Missing TELEGRAM_BOT_TOKEN secret.")
    if not chat_id:
        raise RuntimeError("Missing TELEGRAM_CHAT_ID secret. Example: @YourChannelUsername")

    posts = load_posts()
    post, today, index = choose_daily_post(posts)
    message = build_message(post)

    print(f"Posting date={today}, post_index={index}, chars={len(message)}")
    send_telegram_message(token, chat_id, message)

if __name__ == "__main__":
    main()
