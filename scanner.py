import praw, requests, json, time, os
from datetime import datetime

# Reddit connection - create app at reddit.com/prefs/apps
reddit = praw.Reddit(
    client_id=os.getenv("REDDIT_CLIENT_ID"),
    client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
    user_agent=os.getenv("REDDIT_USER_AGENT")
)

KEYWORDS = ["allowance", "kids allowance", "kids won't save", "ADHD kids money"]
SUBS = ["Parenting", "SingleParents", "personalfinance"]

leads = []

for sub_name in SUBS:
    sub = reddit.subreddit(sub_name)
    for post in sub.new(limit=20):
        if any(k in post.title.lower() for k in KEYWORDS):
            print(f"Found: {post.title}")
            
            # 2 min gap you asked
            time.sleep(120)

            # Ask Ollama to draft answer - free local LLM
            prompt = f"You are a 35yo single mom finance coach. Parent asks: {post.title} - {post.selftext[:300]}. Give 3 line helpful answer, no links, no salesy tone, just value."
            
            r = requests.post("http://localhost:11434/api/generate", json={
                "model": "llama3.2:1b",
                "prompt": prompt,
                "stream": False
            })
            draft = r.json()['response']

            leads.append({
                "time": str(datetime.now()),
                "sub": sub_name,
                "title": post.title,
                "url": post.url,
                "draft_answer": draft
            })

# Save drafts - you manually post from here
with open("data/leads.json", "w") as f:
    json.dump(leads, f, indent=2)

print(f"Done - {len(leads)} drafts saved to data/leads.json")
