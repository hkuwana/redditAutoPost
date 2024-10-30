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
- X-minute delay between posts Right now set to 46 minutes.
- Progress tracking with countdown timer
````

## Reddit Developer API Setup Guide

### Creating Your Reddit App

1. Go to [Reddit App Preferences](https://www.reddit.com/prefs/apps)

2. Click "create another app..." at bottom of page

3. Fill in the app details:
   - **name**: Choose a name for your app
   - **app type**: Select "script"
   - **description**: Brief description of your app
   - **redirect uri**: Use `http://localhost:8080`
   - **about url**: Optional, can leave blank

4. Click "create app"

### Getting Your Credentials

After creation, you'll see your app's details. Note these important values:

- **client_id**: Found under your app name (14 character string)
- **client_secret**: Listed as "secret"

### Updating accounts.json

Add these credentials to your `accounts.json`:
```json
[
  {
    "username": "your_reddit_username",
    "password": "your_reddit_password",
    "client_id": "your_14_char_client_id",
    "client_secret": "your_27_char_secret",
    "target_subreddits": ["subreddit_name"],
    "flair_text": "Flair",
    "profile": {
      "zodiac_sign": "Your_Sign",
      "custom_title": "Your Post Title",
      "description_template": "Your description with [links](URL)"
    }
  }
]
```

### Security Notes

- Never share your client_secret
- Store credentials securely
- Don't commit accounts.json to public repositories