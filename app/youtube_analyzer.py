import os
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
import pandas as pd

# Define API credentials and service
def authenticate_youtube():
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"  # Only for development
    api_service_name = "youtube"
    api_version = "v3"
    client_secrets_file = "credentials.json"

    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
        client_secrets_file, ["https://www.googleapis.com/auth/youtube.readonly"]
    )
    credentials = flow.run_console()
    youtube = googleapiclient.discovery.build(
        api_service_name, api_version, credentials=credentials
    )
    return youtube

# Function to fetch video details based on a keyword or other criteria
def fetch_video_data(youtube, keyword, max_results=10):
    request = youtube.search().list(
        part="snippet",
        q=keyword,
        maxResults=max_results,
        type="video"
    )
    response = request.execute()

    video_data = []
    for item in response.get("items", []):
        video_id = item["id"]["videoId"]
        title = item["snippet"]["title"]
        # You can add more fields as needed, such as view count, likes, etc.
        video_data.append({
            "video_id": video_id,
            "title": title,
        })
    return video_data

# Main execution to fetch data
if __name__ == "__main__":
    youtube = authenticate_youtube()
    keyword = "your_search_keyword"  # e.g., "robotic surgery"
    video_data = fetch_video_data(youtube, keyword)
    df = pd.DataFrame(video_data)
    print(df)
