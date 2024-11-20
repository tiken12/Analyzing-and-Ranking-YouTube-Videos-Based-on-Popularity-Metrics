from nbformat import v4 as nbf

# Define the content for the Google Colab notebook
notebook_content = nbf.new_notebook()

# Add the cells for the notebook
notebook_content.cells = [
    # Add the setup cell
    nbf.new_code_cell("""
# Install required libraries
!pip install transformers youtube-transcript-api pandas
    """),

    # Add the imports and utility functions
    nbf.new_code_cell("""
# Imports and utility functions
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
from youtube_transcript_api import YouTubeTranscriptApi
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer

# Fetch video transcript
def get_video_transcript(video_id):
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        return " ".join([entry['text'] for entry in transcript])
    except Exception as e:
        print(f"Error fetching transcript for video {video_id}: {e}")
        return None

# Generate summary using FLAN-T5
def generate_summary(title, description, transcript=None, iterations=3):
    model_name = "google/flan-t5-large"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSeq2SeqLM.from_pretrained(model_name)

    prompt = f"You are tasked with summarizing a YouTube video titled: '{title}'.\\n"
    if transcript:
        prompt += f"Here is the video transcript:\\n{transcript}\\n"
    prompt += f"The video is about: {description}.\\n"
    prompt += "Write a detailed and engaging summary of at least 200 words.\\n"

    for i in range(iterations):
        inputs = tokenizer(prompt, return_tensors="pt", truncation=True)
        summary_ids = model.generate(
            inputs.input_ids,
            max_length=400,
            min_length=200,
            length_penalty=1.5,
            repetition_penalty=2.0,
            temperature=1.0,
            num_beams=4,
            early_stopping=True
        )
        summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
        prompt = f"Improve this summary:\\n{summary}\\n"
    return summary
    """),

    # Add the ranking function
    nbf.new_code_cell("""
# Keyword relevance
def get_keyword_relevance(summary, keyword):
    vectorizer = CountVectorizer(vocabulary=[keyword])
    relevance_score = vectorizer.fit_transform([summary]).toarray().sum()
    return relevance_score

# Content depth score
def get_content_depth_score(summary, max_words=500):
    word_count = len(summary.split())
    return min(word_count / max_words, 1)

# Ranking function
def rank_videos(video_data, video_stats):
    video_df = pd.DataFrame(video_data)
    stats_df = pd.DataFrame(video_stats)
    merged_df = pd.merge(video_df, stats_df, on="video_id")

    merged_df['transcript'] = merged_df['video_id'].apply(get_video_transcript)
    merged_df['summary'] = merged_df.apply(
        lambda row: generate_summary(row['title'], row['description'], row['transcript']), axis=1
    )
    merged_df['keyword_relevance'] = merged_df['summary'].apply(
        lambda summary: get_keyword_relevance(summary, "your search keyword")
    )
    merged_df['content_depth'] = merged_df['summary'].apply(get_content_depth_score)

    merged_df['score'] = (
        merged_df['views'] * 0.4 +
        merged_df['likes'] * 0.3 +
        merged_df['keyword_relevance'] * 0.2 +
        merged_df['content_depth'] * 0.1
    )
    ranked_videos = merged_df.sort_values(by='score', ascending=False).reset_index(drop=True)
    return ranked_videos
    """),

    # Add example usage cell
    nbf.new_code_cell("""
# Example Usage
video_data = [
    {"video_id": "Ks-_Mh1QhMc", "title": "Example Video 1", "description": "AI tutorials"},
    {"video_id": "dQw4w9WgXcQ", "title": "Example Video 2", "description": "AI basics"}
]
video_stats = [
    {"video_id": "Ks-_Mh1QhMc", "views": 1000, "likes": 50, "comments": 10},
    {"video_id": "dQw4w9WgXcQ", "views": 2000, "likes": 150, "comments": 20}
]

ranked_videos = rank_videos(video_data, video_stats)
print(ranked_videos)
    """)
]

# Save the notebook
notebook_path = "YouTubeAnalyzer_Colab.ipynb"
with open(notebook_path, 'w') as f:
    f.write(nbf.writes(notebook_content))
print(f"Notebook saved as {notebook_path}")
