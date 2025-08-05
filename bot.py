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

# ✅ AI-like random comment generator
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
        "Try out",
        "Check out",
        "Give a shot to",
        "You might like",
        "Have a look at"
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

    comment = f"""{random.choice(greetings)} {random.choice(phrases)}  
{random.choice(endings)} {random.choice(platforms)}  
{random.choice(closers)}  
{random.choice(followup)}"""

    return comment

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

# ✅ Upvote and comment on new posts
def promote_once():
    subreddits = load_subreddits()
    sub = random.choice(subreddits)
    print(f"🔍 Searching in r/{sub}...")

    try:
        subreddit = reddit.subreddit(sub)
        for submission in subreddit.hot(limit=10):
            if not has_already_replied(submission):
                print(f"👍 Liking and 💬 commenting on post: {submission.title}")
                submission.upvote()
                promo_comment = generate_comment()
                submission.reply(promo_comment)
                print(f"✅ Replied with: {promo_comment}\n")
                break
    except APIException as e:
        if "RATELIMIT" in str(e):
            delay = extract_wait_time(str(e))
            print(f"⏳ Rate limited. Sleeping for {delay} seconds...")
            time.sleep(delay)
        else:
            print(f"❌ API Error: {e}")
    except Exception as e:
        print(f"❌ General Error: {e}")

# ✅ Just upvote some random posts to look natural
def upvote_random_posts():
    subreddits = load_subreddits()
    sub = random.choice(subreddits)
    print(f"🎯 Randomly liking posts in r/{sub}...")

    try:
        subreddit = reddit.subreddit(sub)
        for submission in subreddit.hot(limit=5):
            print(f"👍 Upvoting post: {submission.title}")
            submission.upvote()
            time.sleep(random.randint(10, 30))  # short delay between each upvote
    except Exception as e:
        print(f"❌ Error while upvoting in r/{sub}: {e}")

# ✅ Handle Reddit’s rate limit time (e.g. wait for 9 minutes)
def extract_wait_time(error_msg):
    import re
    match = re.search(r"(\d+) minutes?", error_msg)
    if match:
        return int(match.group(1)) * 60
    match = re.search(r"(\d+) seconds?", error_msg)
    if match:
        return int(match.group(1))
    return 600  # default 10 mins

# ✅ Main Loop
if __name__ == "__main__":
    while True:
        action = random.choice(["promote", "upvote"])
        if action == "promote":
            promote_once()
        else:
            upvote_random_posts()

        wait_time = random.randint(1200, 1800)  # 20–30 mins
        print(f"⏸ Sleeping for {wait_time // 60} minutes...\n")
        time.sleep(wait_time)
