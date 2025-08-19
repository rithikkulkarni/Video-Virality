from googleapiclient.discovery import build
from dotenv import load_dotenv
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

load_dotenv()
api_key = os.getenv('YOUTUBE_API_KEY')
youtube = build('youtube', 'v3', developerKey=api_key)

# Example: retrieve video details
def get_video_details(video_id):
    request = youtube.videos().list(part='snippet,statistics', id=video_id)
    response = request.execute()
    return response

def get_video_details_batch(video_ids):
    details = []
    for i in range(0, len(video_ids), 50):
        batch = video_ids[i:i+50]
        req = youtube.videos().list(part='snippet,statistics', id=','.join(batch))
        resp = req.execute()
        details.extend(resp['items'])
    return details

def get_uploads_playlist_id(channel_id):
    resp = youtube.channels().list(part='contentDetails', id=channel_id).execute()
    return resp['items'][0]['contentDetails']['relatedPlaylists']['uploads']

def get_all_video_ids_from_channel(channel_id):
    uploads_playlist_id = get_uploads_playlist_id(channel_id)
    video_ids = []
    next_page_token = None
    while True:
        pl_request = youtube.playlistItems().list(
            part='contentDetails',
            playlistId=uploads_playlist_id,
            maxResults=50,
            pageToken=next_page_token
        )
        pl_response = pl_request.execute()
        for item in pl_response['items']:
            video_ids.append(item['contentDetails']['videoId'])
        next_page_token = pl_response.get('nextPageToken')
        if not next_page_token:
            break
    return video_ids

if __name__ == "__main__":
    channel_ids = [
    "UCsaGKqPZnGp_7N80hcHySGQ",
    "UChBEbMKI1eCcejTtmI32UEw",
    "UCTvYEid8tmg0jqGPDkehc_Q",
    "UCpprBWvibvmOlI8yJOEAAjA",
    "UC4rqhyiTs7XyuODcECvuiiQ",
    "UCj-wTLj0p0YvTkS-9-ACm0A",
    "UCR9Gcq0CMm6YgTzsDxAxjOQ",
    "UC4Ndz98NI_-9VQM3E7fctnQ",
    "UCckPYr9b_iVucz8ID1Q67sw",
    "UCqSeA-rZs6GOfZrs9jZRXtA",
    "UCoxcjq-8xIDTYp3uz647V5A",
    "UC2C_jShtL725hvbm1arSV9w",
    "UCUQo7nzH1sXVpzL92VesANw",
    "UCRix1GJvSBNDpEFY561eSzw",
    "UCc_-hy0u9-oKlNdMKHBudcQ",
    "UCSOpcUkE-is7u7c4AkLgqTw",
    "UC5I2hjZYiW9gZPVkvzM8_Cw",
    "UCVYamHliCI9rw1tHR1xbkfw",
    "UC9fSZHEh6XsRpX-xJc6lT3A",
    "UCzJIliq68IHSn-Kwgjeg2AQ",
    "UC8v4vz_n2rys6Yxpj8LuOBA",
    "UC0KiGuCTrehqzSQ7ikjxSQw",
    "UCnQhwPVwcP-DnbUZtIMrupw",
    "UC0Ize0RLIbGdH5x4wI45G-A",
    "UCXulruMI7BHj3kGyosNa0jA",
    "UCVrvnobbNGGMsS5n2mJwfOg",
    "UCqjwF8rxRsotnojGl4gM0Zw",
    "UCzGLDaTu81nJDtWK10MniGg",
    "UCplkk3J5wrEl0TNrthHjq4Q",
    "UCWrtsravWX0ANhHiJXNlyXw",
    "UCUKi4zY5ETSqrKAjTBgjM-g",
    "UCpIafFPGutTAKOBHMtGen7g",
    "UCzGEGjOCbgv9z9SF71QyI7g",
    "UCE6acMV3m35znLcf0JGNn7Q",
    "UC4v2tQ8GqP0RbmAzhp4IFkQ",
    "UCSbyncU597LMwb3HhnAI_4w",
    "UCMfXv2enRXepxG92VoxfrEg",
    "UC4-CH0epzZpD_ARhxCx6LaQ",
    "UCOpcACMWblDls9Z6GERVi1A"
]
    all_video_details = []
    for channel_id in channel_ids:
        print(f"Processing channel: {channel_id}")
        video_ids = get_all_video_ids_from_channel(channel_id)
        print(f"  Found {len(video_ids)} videos.")
        video_details = get_video_details_batch(video_ids)
        # Add channel_id to each video for reference
        for vid in video_details:
            vid['channel_id'] = channel_id
        all_video_details.extend(video_details)
        print(f"  Retrieved details for {len(video_details)} videos.")

    # Convert all video details to a pandas DataFrame
    df = pd.json_normalize(all_video_details)
    print(df.head())

    # Save DataFrame to CSV
    filename = "test.csv"
    df.to_csv(filename, index=False)
    print(f"Video details saved to {filename}")