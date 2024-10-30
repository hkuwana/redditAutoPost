# Reddit Meme Poster Setup Guide

## Prerequisites

- Python 3.x installed
- Reddit account(s) with API access
- Images for posting

## Installation Steps

1. Create project directory:

   ```bash
   mkdir reddit_poster
   cd reddit_poster
   ```

2. Set up virtual environment:

   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On Mac/Linux:
   source venv/bin/activate
   ```

3. Install required package:

````bash
    pip install praw
    ```

4. Create folder structure:

    ```bash
    mkdir memes
    ```

5. Create `accounts.json`:

    ```json
    [
    {
        "username": "your_username",
        "password": "your_password",
        "client_id": "your_client_id",
        "client_secret": "your_client_secret",
        "target_subreddits": ["subreddit_name"],
        "flair_text": "Flair",
        "profile": {
        "zodiac_sign": "Your_Sign",
        "custom_title": "Your Title",
        "description_template": "Your description with [links](URL)"
        }
    }
    ]
    ```

6. Add images to `memes` folder

7. Run the script:

    ```bash
    python reddit.py
    ```

## Troubleshooting

- If you see websocket errors but posts appear successful, you can ignore these warnings
- Verify your Reddit API credentials if posts fail
- Ensure images are in supported formats (jpg, png)

## Features

- Posts images with custom titles and descriptions
- Supports post flairs
- 15-minute delay between posts
- Progress tracking with countdown timer
````
