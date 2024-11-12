import random
import praw
import os
import json
import time
from datetime import datetime, timedelta
import sys
from typing import Dict, Any, List, Optional

class RedditAccountManager:
    def __init__(self, accounts_file: str = 'accounts.json'):
        with open(accounts_file) as f:
            config = json.load(f)
            
        # Store global settings with defaults
        self.global_settings = config.get('global_settings', {
            'debug_mode': False,
            'delay_minutes': 33,
            'posting_enabled': True
        })
        
        self.accounts = config.get('accounts', [])
        self.last_post_time: Optional[datetime] = None
        
        self.reddit_instances = {}
        for account in self.accounts:
            self.reddit_instances[account['username']] = praw.Reddit(
                client_id=account['client_id'],
                client_secret=account['client_secret'],
                username=account['username'],
                password=account['password'],
                user_agent=f"script:content_poster:v1.0 (by /u/{account['username']})"
            )

    def wait_until_next_slot(self, delay_minutes: int) -> None:
        """Wait until the next available posting slot."""
        if not self.last_post_time:
            self.last_post_time = datetime.now()
            return

        # Calculate when we should post next
        next_post_time = self.last_post_time + timedelta(minutes=delay_minutes)
        current_time = datetime.now()

        # If we need to wait, calculate the wait time
        if next_post_time > current_time:
            wait_seconds = (next_post_time - current_time).total_seconds()
            if wait_seconds > 0:
                print(f"\nWaiting until {next_post_time.strftime('%H:%M:%S')} before next post...")
                self.countdown_timer(int(wait_seconds))

        self.last_post_time = datetime.now()

    @staticmethod
    def countdown_timer(seconds: int) -> None:
        """Display a countdown timer."""
        for remaining in range(seconds, 0, -1):
            sys.stdout.write(f"\rNext post in: {remaining//60:02d}:{remaining%60:02d}")
            sys.stdout.flush()
            time.sleep(1)
        sys.stdout.write("\r" + " " * 30 + "\r")

    def get_flair_id(self, username: str, subreddit_name: str, flair_text: str) -> str | None:
        subreddit = self.reddit_instances[username].subreddit(subreddit_name)
        for flair in subreddit.flair.link_templates:
            if flair['text'].lower() == flair_text.lower():
                return flair['id']
        return None

    def safely_delete_image(self, image_path: str, debug: bool = False) -> None:
        """Safely delete an image file if it exists and we're not in debug mode."""
        if not debug and image_path and os.path.exists(image_path):
            try:
                os.remove(image_path)
                print(f"Deleted image: {image_path}")
            except Exception as e:
                print(f"Error deleting image {image_path}: {str(e)}")

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
        submission = None
        
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
                self.safely_delete_image(content_data['image_path'], debug)
            else:
                submission = subreddit.submit(
                    title=content_data['title'],
                    selftext=content_data['description'],
                    flair_id=flair_id
                )
            
            if content_data.get('description') and content_data.get('image_path'):
                try:
                    submission.reply(content_data['description'])
                except Exception as e:
                    print(f"Error posting comment: {str(e)}")
                    
        except Exception as e:
            if "WebSocket" in str(e) and submission is not None:
                print("WebSocket error encountered but post succeeded.")
                self.safely_delete_image(content_data['image_path'], debug)
                return f"https://reddit.com{submission.permalink}"
            
            print(f"Error posting content: {str(e)}")
            self.safely_delete_image(content_data['image_path'], debug)
            raise e
            
        return f"https://reddit.com{submission.permalink}"

def prepare_content(account: Dict[str, Any], subreddit_config: Dict[str, Any]) -> Dict[str, Any] | None:
    content = {
        'subreddit': subreddit_config['name'],
        'flair_text': subreddit_config.get('flair_text')
    }
    
    title_template = subreddit_config['title_template']
    content['title'] = random.choice(title_template) if isinstance(title_template, list) else title_template

    description_template = subreddit_config['description_template']
    description = random.choice(description_template) if isinstance(description_template, list) else description_template

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
    print("Starting Reddit poster script...")
    
    try:
        manager = RedditAccountManager()
        
        debug_mode = manager.global_settings.get('debug_mode', False)
        delay_minutes = manager.global_settings.get('delay_minutes', 33)
        posting_enabled = manager.global_settings.get('posting_enabled', True)
        
        print(f"Debug mode: {debug_mode}")
        print(f"Delay minutes: {delay_minutes}")
        print(f"Posting enabled: {posting_enabled}")
        
        if not posting_enabled:
            print("Posting is disabled in global settings. Exiting...")
            return
            
        if debug_mode:
            print("Running in debug mode")
            delay_minutes = 0

        post_times = []
        posts_made = 0

        print(f"Processing {len(manager.accounts)} accounts...")

        for account in manager.accounts:
            print(f"\nProcessing account: {account['username']}")
            
            for subreddit_config in account['subreddits']:
                print(f"Processing subreddit: {subreddit_config['name']}")
                
                # Wait for the next available posting slot
                if not debug_mode and posts_made > 0:
                    manager.wait_until_next_slot(delay_minutes)
                
                content = prepare_content(account, subreddit_config)
                if not content:
                    print(f"No content available for {account['username']} in r/{subreddit_config['name']}")
                    continue

                try:
                    url = manager.post_content(account['username'], content, debug=debug_mode)
                    current_time = datetime.now()
                    post_times.append(current_time)
                    posts_made += 1
                    
                    print(f"\nPosted at {current_time.strftime('%H:%M:%S')}")
                    print(f"Posted to r/{content['subreddit']}")
                    print(f"Post URL: {url}")
                    print(f"Posts made so far: {posts_made}")
                    
                except Exception as e:
                    print(f"Error posting as {account['username']}: {str(e)}")

        print("\nAll posts completed!")
        print(f"Total posts made: {posts_made}")
        for i, post_time in enumerate(post_times):
            print(f"Post {i+1}: {post_time.strftime('%H:%M:%S')}")
            
    except Exception as e:
        print(f"Error in main: {str(e)}")
        raise e

if __name__ == "__main__":
    main()