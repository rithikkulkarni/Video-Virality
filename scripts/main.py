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
    "UCNC6uUtrcPGWJJdjol2-uDQ",
    "UCWpN3lA7SFXz297RrexMk7w",
    "UCEZvjCk6yoPOfDWDgiWjnVQ",
    "UCEiui9T4ZYx8K8nuZ5YFSTw",
    "UCI0X6XT0iIT178DIxuhnQ0A",
    "UCszDlhrQpNsUAvhK1ejOr7g",
    "UCHXQQUcC09ayHHXT19WPxmQ",
    "UCSrqpWlxi665eQpT3cQ7faw",
    "UCTUo98NJmvkyP4ltv5W3D9g",
    "UCUYdOka3TBY0OV75AkiuMRw",
    "UCil_aeLn8pzRbNyVF_ENGWQ",
    "UC55EY1hi7yVht5ysukmMscQ",
    "UCPrnZvTrcwqViqmhdRYGY-Q",
    "UCfXpgHHl_zKxNbCK_MszeYQ",
    "UC0HzEBLlJxlrwBAHJ5S9JQg",
    "UCljE1ODdSF7LS9xx9eWq0GQ",
    "UC2av1pwBQwy4mrPVVlWl7-Q",
    "UCzqlzMvlYyWVxFcNMZYzE0g",
    "UCybLjt4Vp59aSXVVcI2RS1w",
    "UCRG_N2uO405WO4P3Ruef9NA",
    "UCV4dQuxfyEHD-JzvT1Ur_jg",
    "UCXh70MDHSrPxLIxmHqN9ttg",
    "UCAJ5ASOAx4sJlMIA1L7TE8g",
    "UCGKfVunhAgXOoYru_7LzMjg",
    "UC8_1TYtupQV27GXQSLHtg3w",
    "UC-4oG9m_uiiFiBU3hsyl2uQ",
    "UCaaCrr_lZjK1OydGJ87Y_hA",
    "UCpWKp6lHakdUNsy49_TLDzA",
    "UCS7wVohIwd66b95xyuw7DFQ",
    "UCOmXfX6mwaEtTAVXkzpdhvQ",
    "UC96TGOrWeIWxr6noks2ipzw",
    "UCCDlc0Nw29RmqOs2jQPEX6A",
    "UCtNlZNCDnPPw3tImEboXo_w",
    "UCKXAIClK1ZpQ0irkJZH00dg",
    "UCR2-F1UWmLeNgKEjfYnLibQ",
    "UC-MtmLd4PbmNuRaasDgBFBA",
    "UChajkcPS2cwubmrykAvTqpA",
    "UC9l0mKCZRMJCZ-UFwDgrUjw",
    "UC53ONFvWH0hU985xkjVLSwQ",
    "UChKkEDkpHs5M5Glpx8ubztg",
    "UCZxtOYSWDb8wogyDqVAiOBA",
    "UC7pBv8EE3FtDZEF3HtnbFjA",
    "UCOw0zA-Gf5gpQ6K446mR0wA",
    "UCGku32OWE9nnRKrJiA4UlKA",
    "UC_elPuYZ3vWE0QV_WMnYoSw"
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
    filename = "group6_v2.csv"
    df.to_csv(filename, index=False)
    print(f"Video details saved to {filename}")