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
        # 'UC0lG3Ihe4LGV851lODRIS5g', # French Cooking Academy
        # 'UCscCA-entvtKdjmVF46mz-w', # Cooking Buddies
        # 'UC96HuwJhXI2p-_zZi3oAR_g', # Glock9
        # 'UCaOqw1VxoohgWyifBcZ39Kg', # Phisnom
        # 'UCt_t6FwNsqr3WWoL6dFqG9w', # BrainCraft
        # 'UC1H1NWNTG2Xi3pt85ykVSHA', # Jordan Harrod
        # 'UC7qPftDWPw9XuExpSgfkmJQ', # Nostalgia Nerd
        # 'UC2DjFE7Xf11URZqWBigcVOQ', # EEVblog
        # 'UCwg9GXj-BUwfZkPG4Nm2gUQ', # Lainey Ostrom
        # 'UC3fgv-ejI64Gw3FzastFIpw', # Kristin Johns
        # 'UCwuLoOntr78Ab37BuntMWEg', # iGoBart
        # 'UCJfm-feI6sSoaDwFx_viN1g', # Ghib Ojisan
        # 'UCh_w_vLvlZNBeTAP8qaWhoA', # Vo2maxProductions
        # 'UCOpsZxrmeDARilha1uq4slA', # Heather Robertson
        # 'UCEi0EgWJ5m7gVBQ68a1L0TA', # Alexrainbirdmusic
        # 'UC4i0urwpMIEYdtJWU7hlu2g', # Megan Davies
        # 'UCkEXXbo1QOTesV8h2hkN-1g', # The Valleyfolk
        # 'UCghR6gNuBneEKkDuKtXQM4w', # Chris Fleming
        # 'UCEn3fRj2e0mpqYsijxnzayg', # Xyla Foxlin
        # 'UCljE1ODdSF7LS9xx9eWq0GQ', # Potholer54
        # 'UCA8P3Rgfjn0IFZL4bmrKbrg', # Rule1Investing
        # 'UCDXTQ8nWmx_EhZ2v-kp7QxA', # Ben Felix
        # 'UCweYFCSaqh3bRnM5M7_KUUg', # Griffon Ramsey
        # 'UClM2LuQ1q5WEc23462tQzBg', # Proko
        # 'UCiFOL6V9KbvxfXvzdFSsqCw', # Ken
        # 'UCPmCaKjzYF3pXYLfaRhacwA', # Kassia
        # 'UCNEI-oWOivQJ9IMn8GeCrMg', # Gabriel Piano
        # 'UCgx_iANJu2vdqaVldHn94vg', # TDunc Piano
        # 'UCIf54-aXt1pqliaehOHX-ow', # RB Music Piano
        'UCUyAA4Ekq5nHmr5mjZ-L4eA', # Clips Joy
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
    filename = "clipsjoy.csv"
    df.to_csv(filename, index=False)
    print(f"Video details saved to {filename}")