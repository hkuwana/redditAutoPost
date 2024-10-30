import praw
import os
import json
import time
from datetime import datetime
import sys

class RedditAccountManager:
    def __init__(self, accounts_file: str = 'accounts.json'):
        with open(accounts_file) as f:
            self.accounts = json.load(f)
        
        self.reddit_instances = {}
        for account in self.accounts:
            self.reddit_instances[account['username']] = praw.Reddit(
                client_id=account['client_id'],
                client_secret=account['client_secret'],
                username=account['username'],
                password=account['password'],
                user_agent=f"script:meme_poster:v1.0 (by /u/{account['username']})"
            )

    def get_flair_id(self, username: str, subreddit_name: str, flair_text: str) -> str:
        """Get flair ID by matching flair text"""
        subreddit = self.reddit_instances[username].subreddit(subreddit_name)
        for flair in subreddit.flair.link_templates:
            if flair['text'].lower() == flair_text.lower():
                return flair['id']
        return None

    def post_meme(self, username: str, subreddit: str, image_path: str, 
                  title: str, description: str = None, flair_text: str = None) -> str:
        reddit = self.reddit_instances[username]
        subreddit_obj = reddit.subreddit(subreddit)
        
        # Get flair ID if flair_text provided
        flair_id = None
        if flair_text:
            flair_id = self.get_flair_id(username, subreddit, flair_text)
            if not flair_id:
                print(f"Warning: Flair '{flair_text}' not found in r/{subreddit}")

        # Submit with flair
        submission = subreddit_obj.submit_image(
            title=title,
            image_path=image_path,
            flair_id=flair_id
        )
        
        if description:
            submission.reply(description)
            
        return f"https://reddit.com{submission.permalink}"

    def format_title(self, base_title: str, profile: dict) -> str:
        return base_title.format(**profile)

    def format_description(self, base_description: str, profile: dict) -> str:
        return base_description.format(**profile)

# [Previous countdown_timer function remains the same]

def main():
    manager = RedditAccountManager()
    memes_folder = "memes"
    meme_files = sorted(os.listdir(memes_folder))
    post_times = []
    delay_minutes = 15

    for i, account in enumerate(manager.accounts):
        if i > 0:
            print(f"\nWaiting {delay_minutes} minutes before next post...")
            countdown_timer(delay_minutes)
            
        if not meme_files:
            print("No more memes to post!")
            break

        meme = meme_files[0]
        meme_path = os.path.join(memes_folder, meme)
        current_time = datetime.now()
        post_times.append(current_time)
        subreddit = account['target_subreddits'][0]

        try:
            title = manager.format_title(
                "Any other {zodiac_sign}s feel this way? {custom_title}",
                account['profile']
            )
            
            description = manager.format_description(
                account['profile']['description_template'],
                account['profile']
            )

            url = manager.post_meme(
                username=account['username'],
                subreddit=subreddit,
                image_path=meme_path,
                title=title,
                description=description,
                flair_text=account.get('flair_text')  # Get flair from account config
            )
            print(f"\nPosted at {current_time.strftime('%H:%M:%S')}")
            print(f"Posted {meme} to r/{subreddit} using {account['username']}: {url}")
            
            meme_files.pop(0)
            
        except Exception as e:
            print(f"\nError posting as {account['username']}: {str(e)}")

    print("\nAll posts completed!")
    for i, post_time in enumerate(post_times):
        print(f"Post {i+1}: {post_time.strftime('%H:%M:%S')}")

if __name__ == "__main__":
    main()