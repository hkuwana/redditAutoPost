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

   ```bash
   pip install praw
   ```

4. Create folder structure:

   ```bash
   mkdir images
   ```

5. Create `accounts.json`:

   ```json
   [
     {
       "username": "your_username",
       "password": "your_password",
       "client_id": "your_client_id",
       "client_secret": "your_client_secret",
       "profile": {
         "content_type": "meme"
       },
       "subreddits": [
         {
           "name": "subreddit_name",
           "flair_text": "Your_Flair",
           "title_template": "Your Post Title",
           "description_template": "Your description with [links](URL)"
         }
       ]
     }
   ]
   ```

7. Add images to `images` folder

8. Run the script:

   ```bash
   python reddit.py
   ```

## Troubleshooting

- If you see websocket errors but posts appear successful, these can be ignored - images will still be deleted after successful posting
- Verify your Reddit API credentials if posts fail
- Ensure images are in supported formats (jpg, png, gif)

## Features

- Posts images with custom titles and descriptions
- Supports post flairs
- 26-minute delay between posts
- Progress tracking with countdown timer
- Debug mode for testing
- Handles WebSocket connection errors gracefully
- Automatic cleanup of posted images

## Reddit Developer API Setup

### Creating Your Reddit App

1. Go to [Reddit App Preferences](https://www.reddit.com/prefs/apps)
2. Click "create another app..." at bottom
3. Fill in details:
   - **name**: Choose app name
   - **app type**: Select "script"
   - **description**: Brief app description
   - **redirect uri**: Use `http://localhost:8080`
   - **about url**: Optional

4. Click "create app"

### Getting Your Credentials

After creation, note these values:

- **client_id**: Found under app name (14 character string)
- **client_secret**: Listed as "secret"

### Security Notes

- Never share your client_secret
- Store credentials securely
- Don't commit accounts.json to public repositories
