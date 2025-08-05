import praw
import time
import random
import os
from praw.exceptions import APIException
from dotenv import load_dotenv

# ✅ Load environment variables from .env
load_dotenv()

# ✅ Reddit Auth Setup
reddit = praw.Reddit(
    client_id=os.getenv("REDDIT_CLIENT_ID"),
    client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
    username=os.getenv("REDDIT_USERNAME"),
    password=os.getenv("REDDIT_PASSWORD"),
    user_agent="TWS Promo Bot by u/" + os.getenv("REDDIT_USERNAME")
)

# ✅ AI-style randomized comment
def generate_comment():
    greetings = ["Hey!", "Hi there!", "Yo!", "Hello!", "What's up!"]
    phrases = [
        "Feeling stuck, bored, or just want to talk?",
        "Looking to meet someone interesting today?",
        "Bored and need to chat with a stranger?",
        "Want to talk to someone new?",
        "Need to vent or connect anonymously?"
    ]
    endings = [
        "Try out", "Check out", "Give a shot to", "You might like", "Have a look at"
    ]
    platforms = [
        "**[TalkWithStranger](https://talkwithstranger.com)**",
        "**[TWS - TalkWithStranger](https://talkwithstranger.com)**",
        "**[talkwithstranger.com](https://talkwithstranger.com)**"
    ]
    closers = [
        "Totally free & anonymous. 🌐 No signup needed.",
        "It's global, free, and requires no account. 🌍",
        "100% free, anonymous & no signup required.",
        "Just click and start chatting — no login! 🔒",
        "Meet new people instantly without signing up!"
    ]
    followup = [
        "Let me know how your experience was!",
        "Would love to hear your thoughts if you try it.",
        "Happy chatting! 😊",
        "Hope you enjoy it!",
        "Chat safe & have fun!"
    ]

    components = [
        random.choice(greetings),
        random.choice(phrases),
        random.choice(endings),
        random.choice(platforms),
        random.choice(closers),
        random.choice(followup)
    ]
    random.shuffle(components)
    return " ".join(components)

# ✅ Load subreddits from file
def load_subreddits():
    with open("subreddits.txt", "r") as f:
        return [line.strip() for line in f if line.strip()]

# ✅ Check if already replied to the post
def has_already_replied(submission):
    submission.comments.replace_more(limit=0)
    for comment in submission.comments:
        if comment.author == reddit.user.me():
            return True
    return False

# ✅ Perform a comment
def do_comment():
    subreddits = load_subreddits()
    sub = random.choice(subreddits)
    print(f"💬 Comment task in r/{sub}")

    try:
        subreddit = reddit.subreddit(sub)
        posts = list(subreddit.hot(limit=10))
        random.shuffle(posts)

        for post in posts:
            if not has_already_replied(post):
                comment_text = generate_comment()
                post.reply(comment_text)
                print(f"✅ Commented on: {post.title}")
                print(f"📝 Comment: {comment_text}")
                return
    except APIException as e:
        if "RATELIMIT" in str(e):
            delay = extract_wait_time(str(e))
            print(f"⏳ Rate limited for comment. Sleeping {delay} sec...")
            time.sleep(delay)
        else:
            print(f"❌ API Error during comment: {e}")
    except Exception as e:
        print(f"❌ General Error during comment: {e}")

# ✅ Perform an upvote
def do_upvote():
    subreddits = load_subreddits()
    sub = random.choice(subreddits)
    print(f"👍 Upvote task in r/{sub}")

    try:
        subreddit = reddit.subreddit(sub)
        posts = list(subreddit.hot(limit=10))
        random.shuffle(posts)

        for post in posts:
            print(f"👍 Upvoting: {post.title}")
            post.upvote()
            return
    except Exception as e:
        print(f"⚠️ Upvote error: {e}")

# ✅ Rate limit parser
def extract_wait_time(error_msg):
    import re
    match = re.search(r"(\d+) minutes?", error_msg)
    if match:
        return int(match.group(1)) * 60
    match = re.search(r"(\d+) seconds?", error_msg)
    if match:
        return int(match.group(1))
    return 600

# ✅ Main scheduler
if __name__ == "__main__":
    print("🚀 Reddit Promo Bot started. Running every 30 minutes (6 tasks, 5 min each).")
    while True:
        print("\n🕒 Starting new 30-minute promotion cycle...\n")

        # 1. Comment first
        do_comment()
        time.sleep(300)  # 5 min

        # 2–6. Then 5 upvotes
        for _ in range(5):
            do_upvote()
            time.sleep(300)  # 5 min

        print("\n⏸ 30-minute cycle complete. Starting again...\n")
