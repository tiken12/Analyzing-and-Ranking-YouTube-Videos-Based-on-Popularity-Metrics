from flask import Flask, render_template, request, jsonify
from youtube_analyzer import authenticate_youtube, fetch_video_data, fetch_video_details, rank_videos

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    keyword = request.form.get('keyword')
    max_results = int(request.form.get('max_results', 10))

    youtube = authenticate_youtube()
    video_data = fetch_video_data(youtube, keyword, max_results)
    video_ids = [video['video_id'] for video in video_data]
    video_stats = fetch_video_details(youtube, video_ids)

    # Call the updated rank_videos function
    ranked_videos = rank_videos(video_data, video_stats)

    # Return the top results as JSON
    return jsonify(ranked_videos.to_dict(orient="records"))



if __name__ == "__main__":
    app.run(debug=True)
