from datetime import time
import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

from googleapiclient.discovery import build
import pandas as pd
import torch
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

# Set up YouTube API
api_key = 'AIzaSyDAt3NPgwcke--N5Gj9V7QHMI32YyeYWUM'
youtube = build('youtube', 'v3', developerKey=api_key)

# Function to fetch video details
def fetch_video_details(video_ids):
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
            'views': int(item['statistics'].get('viewCount', 0)),
            'likes': int(item['statistics'].get('likeCount', 0)),
            'comments': int(item['statistics'].get('commentCount', 0))
        }
        video_data.append(video_info)
    return pd.DataFrame(video_data)

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

# Summarization using FLAN-T5
def summarize_video(title, description):
    model_name = "google/flan-t5-large"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSeq2SeqLM.from_pretrained(model_name)

    input_text = f"summarize: Title: {title} Description: {description}"
    inputs = tokenizer(input_text, return_tensors="pt", truncation=True)

    summary_ids = model.generate(inputs.input_ids, max_length=100, min_length=25, length_penalty=2.0)
    summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
    return summary

# Display function with Streamlit
import streamlit as st

def display_top_videos(df):
    st.title("Top 10 YouTube Videos by Popularity Metrics")
    st.write("### Top 10 Videos")
    for index, row in df.head(10).iterrows():
        st.subheader(f"{index + 1}. {row['title']}")
        st.write(f"Views: {row['views']}, Likes: {row['likes']}, Comments: {row['comments']}")
        st.write(f"Summary: {row['summary']}")
        st.write("---")

# Main execution block
video_ids = ['Ks-_Mh1QhMc', 'dQw4w9WgXcQ']  # Example valid YouTube video IDs
video_data = fetch_video_details(video_ids)

if video_data.empty:
    print("No video data available. Please check the video IDs and try again.")
else:
    clean_video_data = clean_data(video_data)
    ranked_video_data = rank_videos(clean_video_data)

    # Apply summarization for each video
    ranked_video_data['summary'] = ranked_video_data.apply(lambda row: summarize_video(row['title'], row['title']), axis=1)
    print(ranked_video_data)

    # Optional: display in Streamlit
    display_top_videos(ranked_video_data)

    # Measure response time
    import time
    start_time = time.time()
    ranked_video_data = rank_videos(clean_video_data)
    response_time = time.time() - start_time
    print(f"Response time: {response_time:.2f} seconds")
