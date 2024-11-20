import os
import time
import pandas as pd
import streamlit as st
from googleapiclient.discovery import build
from youtube_transcript_api import YouTubeTranscriptApi
import requests

# Set up YouTube API
api_key = 'AIzaSyDAt3NPgwcke--N5Gj9V7QHMI32YyeYWUM'
youtube = build('youtube', 'v3', developerKey=api_key)

# Hugging Face API setup
HF_API_URL = "https://api-inference.huggingface.co/models/google/flan-t5-large"
HF_API_TOKEN = "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"
headers = {"Authorization": f"Bearer {HF_API_TOKEN}"}

# Function to fetch video IDs based on a search query
def fetch_video_ids(keyword, max_results=50):
    try:
        request = youtube.search().list(
            q=keyword,
            part="id",
            maxResults=max_results,
            type="video"
        )
        response = request.execute()
        return [item['id']['videoId'] for item in response['items']]
    except Exception as e:
        st.error(f"Error fetching video IDs: {e}")
        return []

# Function to fetch video details
def fetch_video_details(video_ids):
    try:
        request = youtube.videos().list(
            part="snippet,statistics",
            id=','.join(video_ids)
        )
        response = request.execute()
        video_data = []
        for item in response['items']:
            video_info = {
                'video_id': item['id'],
                'title': item['snippet']['title'],
                'description': item['snippet']['description'],
                'views': int(item['statistics'].get('viewCount', 0)),
                'likes': int(item['statistics'].get('likeCount', 0)),
                'comments': int(item['statistics'].get('commentCount', 0))
            }
            video_data.append(video_info)
        return pd.DataFrame(video_data)
    except Exception as e:
        st.error(f"Error fetching video details: {e}")
        return pd.DataFrame()

# Function to fetch video transcript
def get_video_transcript(video_id):
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        return " ".join([entry['text'] for entry in transcript])
    except Exception as e:
        print(f"Error fetching transcript for video {video_id}: {e}")
        return None

# Data cleaning function
def clean_data(df):
    df.fillna(0, inplace=True)
    df[['views', 'likes', 'comments']] = df[['views', 'likes', 'comments']].astype(int)
    return df

# Ranking function
def rank_videos(df):
    df['score'] = df['views'] * 0.5 + df['likes'] * 0.3 + df['comments'] * 0.2
    ranked_videos = df.sort_values(by='score', ascending=False).reset_index(drop=True)
    return ranked_videos

# Summarization using Hugging Face Inference API
def generate_summary(title, description, transcript=None):
    """
    Generates a summary using the Hugging Face Inference API.
    """
    # Construct the prompt
    prompt = f"""
    Summarize the YouTube video titled: "{title}".
    The video is described as: "{description}".
    """
    if transcript:
        prompt += f"""
        Here is an excerpt from the video transcript:
        {transcript[:500]}  # Limit transcript length
        """
    prompt += """
    Write a detailed, engaging summary that is at least 200 words long. 
    Highlight the key points, unique content, and examples covered in the video. 
    Avoid repeating sentences or phrases and ensure coherence and relevance.
    """

    # Send request to Hugging Face API
    payload = {
        "inputs": prompt,
        "parameters": {
            "max_length": 400,       # Allow for longer summaries
            "min_length": 200,       # Ensure summaries are sufficiently detailed
            "temperature": 0.5,      # Make the output more deterministic
            "repetition_penalty": 3.0,  # Strongly discourage repetitive text
            "top_p": 0.9,            # Nucleus sampling to limit randomness
            "num_beams": 4           # Beam search to improve coherence
        },
    }
    response = requests.post(HF_API_URL, headers=headers, json=payload)

    try:
        response_data = response.json()
        if isinstance(response_data, list):  # Handle response as a list
            return response_data[0].get("generated_text", "No summary generated.")
        elif isinstance(response_data, dict):  # Handle response as a dictionary
            return response_data.get("generated_text", "No summary generated.")
        else:
            return "Unexpected response format."
    except Exception as e:
        print(f"Error parsing summary response: {e}")
        return "Error generating summary."


# Streamlit UI
def display_top_videos(df):
    st.title("Top YouTube Videos by Popularity Metrics")
    st.write("### Top Videos")
    for index, row in df.iterrows():
        st.subheader(f"{index + 1}. {row['title']}")
        st.write(f"Views: {row['views']}, Likes: {row['likes']}, Comments: {row['comments']}")
        st.write(f"Summary: {row['summary']}")
        st.write(f"[Watch Video](https://www.youtube.com/watch?v={row['video_id']})")
        st.write("---")

# Main execution block
st.sidebar.title("YouTube Video Analyzer")
search_keyword = st.sidebar.text_input("Search Keyword", "AI Tutorials")
max_results = st.sidebar.slider("Number of Results", 1, 50, 10)

if st.sidebar.button("Analyze"):
    with st.spinner("Fetching video data..."):
        video_ids = fetch_video_ids(search_keyword, max_results)
        if not video_ids:
            st.error("No videos found. Please try a different keyword.")
        else:
            video_data = fetch_video_details(video_ids)
            if video_data.empty:
                st.error("Failed to fetch video details. Try again.")
            else:
                # Add transcripts
                video_data['transcript'] = video_data['video_id'].apply(get_video_transcript)
                
                # Clean and rank data
                clean_video_data = clean_data(video_data)
                ranked_video_data = rank_videos(clean_video_data)

                # Apply summarization for each video
                ranked_video_data['summary'] = ranked_video_data.apply(
                    lambda row: generate_summary(row['title'], row['description'], row['transcript']), axis=1
                )

                # Display results
                display_top_videos(ranked_video_data)

                # Measure response time
                start_time = time.time()
                rank_videos(clean_video_data)
                response_time = time.time() - start_time
                st.sidebar.write(f"Response time: {response_time:.2f} seconds")