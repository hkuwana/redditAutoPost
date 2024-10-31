import random
import praw
import os
import json
import time
from datetime import datetime
import sys
from typing import Dict, Any

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
                user_agent=f"script:content_poster:v1.0 (by /u/{account['username']})"
            )

    def get_flair_id(self, username: str, subreddit_name: str, flair_text: str) -> str | None:
        subreddit = self.reddit_instances[username].subreddit(subreddit_name)
        for flair in subreddit.flair.link_templates:
            if flair['text'].lower() == flair_text.lower():
                return flair['id']
        return None

    def post_content(self, username: str, content_data: Dict[str, Any], debug: bool = False) -> str:
        if debug:
            print(f"\nUsername: {username}")
            print(f"Subreddit: {content_data['subreddit']}")
            print(f"Title: {content_data['title']}")
            print(f"Image path: {content_data.get('image_path', 'None')}")
            print(f"Description: {content_data['description']}")
            print(f"Flair: {content_data.get('flair_text', 'None')}")
            return "DEBUG_URL"

        reddit = self.reddit_instances[username]
        subreddit = reddit.subreddit(content_data['subreddit'])
        
        flair_id = None
        if content_data.get('flair_text'):
            flair_id = self.get_flair_id(username, content_data['subreddit'], content_data['flair_text'])

        try:
            if content_data.get('image_path'):
                submission = subreddit.submit_image(
                    title=content_data['title'],
                    image_path=content_data['image_path'],
                    flair_id=flair_id
                )
            else:
                submission = subreddit.submit(
                    title=content_data['title'],
                    selftext=content_data['description'],
                    flair_id=flair_id
                )
            
            # If we got here, submission was successful
            if content_data.get('image_path') and not debug:
                os.remove(content_data['image_path'])
                
            if content_data.get('description') and content_data.get('image_path'):
                try:
                    submission.reply(content_data['description'])
                except Exception as e:
                    print(f"Error posting comment: {str(e)}")
                    
        except Exception as e:
            if "WebSocket" in str(e) and submission is not None:
                # Post was successful despite WebSocket error
                if content_data.get('image_path') and not debug:
                    os.remove(content_data['image_path'])
                return f"https://reddit.com{submission.permalink}"
            raise e
                
        return f"https://reddit.com{submission.permalink}"

def countdown_timer(minutes: int):
    for remaining in range(minutes * 60, 0, -1):
        sys.stdout.write(f"\rNext post in: {remaining//60:02d}:{remaining%60:02d}")
        sys.stdout.flush()
        time.sleep(1)
    sys.stdout.write("\r" + " " * 30 + "\r")

def prepare_content(account: Dict[str, Any]) -> Dict[str, Any] | None:
    subreddit_config = account['subreddits'][0]
    content = {
        'subreddit': subreddit_config['name'],
        'flair_text': subreddit_config.get('flair_text')
    }
    
    # Handle title selection
    title_template = subreddit_config['title_template']
    content['title'] = random.choice(title_template) if isinstance(title_template, list) else title_template

    # Handle description selection
    description_template = subreddit_config['description_template']
    description = random.choice(description_template) if isinstance(description_template, list) else description_template

    # Replace hyperlink if exists
    hyperlink = account['profile'].get('hyperlink', '')
    content['description'] = description.format(hyperlink=hyperlink)

    if account['profile']['content_type'] == 'meme':
        folder_name = f"{subreddit_config['name']}-images"
        if not os.path.exists(folder_name):
            os.makedirs(folder_name)
            print(f"Created folder: {folder_name}")
            return None

        images = sorted([f for f in os.listdir(folder_name) if f.lower().endswith(('.jpg', '.png', '.gif'))])
        if not images:
            return None
            
        content['image_path'] = os.path.join(folder_name, images[0])

    return content  

def main():
    manager = RedditAccountManager()
    post_times = []
    delay_minutes = 26
    debug_mode = False # Turn to False when posting 
    
    if debug_mode:
        delay_minutes = 0

    for i, account in enumerate(manager.accounts):
        if i > 0:
            countdown_timer(delay_minutes)
        
        content = prepare_content(account)
        if not content:
            print(f"No content available for {account['username']}")
            continue

        current_time = datetime.now()
        post_times.append(current_time)

        try:
            url = manager.post_content(account['username'], content, debug=debug_mode)
            print(f"\nPosted at {current_time.strftime('%H:%M:%S')}")
            print(f"Posted to r/{content['subreddit']}")
            print(f"Post URL: {url}")
            
        except Exception as e:
            print(f"Error posting as {account['username']}: {str(e)}")

    print("\nAll posts completed!")
    for i, post_time in enumerate(post_times):
        print(f"Post {i+1}: {post_time.strftime('%H:%M:%S')}")

if __name__ == "__main__":
    main()