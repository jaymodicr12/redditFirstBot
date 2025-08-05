import praw
import time
import random
import os
from praw.exceptions import APIException
from dotenv import load_dotenv

# ✅ Load environment variables
load_dotenv()

reddit = praw.Reddit(
    client_id=os.getenv("REDDIT_CLIENT_ID"),
    client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
    username=os.getenv("REDDIT_USERNAME"),
    password=os.getenv("REDDIT_PASSWORD"),
    user_agent="TWS Promo Bot by u/" + os.getenv("REDDIT_USERNAME")
)

# ✅ Generate randomized comment
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

# ✅ Load subreddits list
def load_subreddits():
    with open("subreddits.txt", "r") as f:
        return [line.strip() for line in f if line.strip()]

# ✅ Check if bot already replied
def has_already_replied(submission):
    submission.comments.replace_more(limit=0)
    for comment in submission.comments:
        if comment.author == reddit.user.me():
            return True
    return False

# ✅ Logging time countdown
def log_progress(seconds, task_name):
    for remaining in range(seconds, 0, -60):
        mins = remaining // 60
        print(f"⏳ {task_name} starting in {mins} min(s)...")
        time.sleep(60)

# ✅ Commenting task
def do_comment():
    print("🚀 Task 1/6: COMMENT starting...")
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
        print("⚠️ No suitable post to comment on.")
    except APIException as e:
        if "RATELIMIT" in str(e):
            delay = extract_wait_time(str(e))
            print(f"⏳ Rate limited for comment. Sleeping {delay} sec...")
            time.sleep(delay)
        else:
            print(f"❌ API Error during comment: {e}")
    except Exception as e:
        print(f"❌ General Error during comment: {e}")
    print("✅ Comment task complete.\n")

# ✅ Upvote task
def do_upvote(task_num):
    print(f"🚀 Task {task_num}/6: UPVOTE starting...")
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
            break
    except Exception as e:
        print(f"⚠️ Upvote error: {e}")
    print(f"✅ Upvote task {task_num} complete.\n")

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

# ✅ Main Loop
if __name__ == "__main__":
    print("🎯 Reddit Promo Bot launched. 30-min cycle: 1 comment + 5 upvotes (every 5 mins).")
    while True:
        print("\n🔄 Starting new 30-minute cycle...\n")

        # Task 1: Comment
        do_comment()
        log_progress(300, "Upvote Task 2")

        # Tasks 2–6: Upvotes every 5 min
        for i in range(2, 7):
            do_upvote(i)
            log_progress(300, f"Upvote Task {i+1 if i < 6 else 'Restart'}")

        print("✅ 30-minute cycle complete. Restarting...\n")
