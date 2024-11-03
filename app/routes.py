# Defines routes for handling requests
from flask import Blueprint, render_template, request, jsonify
from .youtube_analyzer import authenticate_youtube, fetch_video_data, fetch_video_details, rank_videos

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/api/analyze', methods=['POST'])
def analyze():
    data = request.get_json()
    keyword = data.get('keyword')
    max_results = int(data.get('max_results', 10))

    youtube = authenticate_youtube()
    video_data = fetch_video_data(youtube, keyword, max_results)
    video_ids = [video['video_id'] for video in video_data]
    video_stats = fetch_video_details(youtube, video_ids)

    ranked_videos = rank_videos(video_data, video_stats).head(10)
    return jsonify(ranked_videos.to_dict(orient="records"))
