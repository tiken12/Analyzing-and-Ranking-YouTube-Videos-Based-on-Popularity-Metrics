import pandas as pd
from main import generate_summary
from youtube_transcript_api import YouTubeTranscriptApi
from sklearn.feature_extraction.text import CountVectorizer

# Keyword Relevance
def get_keyword_relevance(summary, keyword):
    vectorizer = CountVectorizer(vocabulary=[keyword])
    relevance_score = vectorizer.fit_transform([summary]).toarray().sum()
    return relevance_score

# Content Depth
def get_content_depth_score(summary, max_words=500):
    word_count = len(summary.split())
    return min(word_count / max_words, 1)

# Fetch transcripts
def get_video_transcript(video_id):
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        print( " ".join([entry['text'] for entry in transcript]))
        return " ".join([entry['text'] for entry in transcript])
    except Exception as e:
        return None

# Ranking Videos
def rank_videos(video_data, video_stats):
    video_df = pd.DataFrame(video_data)
    stats_df = pd.DataFrame(video_stats)
    merged_df = pd.merge(video_df, stats_df, on="video_id")

    # Fetch transcripts and generate summaries
    merged_df['transcript'] = merged_df['video_id'].apply(get_video_transcript)
    merged_df['summary'] = merged_df.apply(
        lambda row: generate_summary(row['title'], row['title'], row['transcript']), axis=1
    )

    # Calculate features
    merged_df['keyword_relevance'] = merged_df['summary'].apply(
        lambda summary: get_keyword_relevance(summary, "your search keyword")
    )
    merged_df['content_depth'] = merged_df['summary'].apply(get_content_depth_score)

    # Calculate ranking score
    merged_df['score'] = (
        merged_df['views'] * 0.4 +
        merged_df['likes'] * 0.3 +
        merged_df['keyword_relevance'] * 0.2 +
        merged_df['content_depth'] * 0.1
    )

    # Return ranked videos
    return merged_df.sort_values(by='score', ascending=False).reset_index(drop=True)
