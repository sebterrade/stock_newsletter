from googleapiclient.discovery import build
import isodate
from . import config

try:
    youtube = build('youtube', 'v3', developerKey=config.API_KEY_YOUTUBE)
except Exception as e:
    print(f"Error initializing YouTube API: {e}")
    youtube = None

class Youtube:

    #Return Channel ID
    @staticmethod
    def get_channel_id(custom_url):
        if not youtube:
            return None
            
        try:
            response = youtube.search().list(
                q=custom_url,
                type='channel',
                part='id',
                maxResults=1
            ).execute()
            
            if response['items']:
                return response['items'][0]['id']['channelId']
        except Exception as e:
            print(f"Error fetching channel ID for {custom_url}: {e}")
            
        return None    
    
    #Get latest Youtube video (5 mins +) from channel
    @staticmethod
    def get_latest_video(channel_id):
        if not youtube:
            return None, None

        try:
            response = youtube.search().list(
                channelId=channel_id,
                order='date',
                type='video',
                part='id',
                maxResults=10
            ).execute()

            video_ids = [item['id']['videoId'] for item in response['items']]

            if not video_ids:
                return None, None

            video_data = youtube.videos().list(
                id=','.join(video_ids),
                part='contentDetails,snippet'
            ).execute()

            for video in video_data['items']:
                duration = isodate.parse_duration(video['contentDetails']['duration']).total_seconds()
                if duration >= 300:  # Not a short
                    title = video['snippet']['title']
                    video_id = video['id']
                    return f"https://www.youtube.com/watch?v={video_id}", title
        except Exception as e:
            print(f"Error fetching videos for channel {channel_id}: {e}")

        return None, None  # No regular video found