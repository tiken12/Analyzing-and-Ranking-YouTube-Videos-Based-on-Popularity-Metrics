# Defines routes for handling requests
from flask import Flask, render_template, request, jsonify
from .youtube_analyzer import authenticate_youtube, fetch_video_data, fetch_video_details, rank_videos
#from app.youtube_analyzer import authenticate_youtube, fetch_video_data, fetch_video_details, rank_videos

#main = Blueprint('main', __name__)

#@main.route('/')
#def index():
#    return render_template('index.html')


app = Flask(__name__)

# Home route to render the UI
@app.route('/')
def home():
    return render_template('index.html')

#@main.route('/api/analyze', methods=['POST'])

# Route to get and rank videos based on the user's search term
@app.route('/analyze', methods=['POST'])
def analyze():
    #data = request.get_json()
    #keyword = data.get('keyword')
    #max_results = int(data.get('max_results', 10))
    keyword = request.form.get('keyword')
    max_results = int(request.form.get('max_results', 10))

    # Authenticate YouTube API and get data
    youtube = authenticate_youtube()
    video_data = fetch_video_data(youtube, keyword, max_results)
    video_ids = [video['video_id'] for video in video_data]
    video_stats = fetch_video_details(youtube, video_ids)

    # Rank videos based on views
    ranked_videos = rank_videos(video_data, video_stats).head(10)
    return jsonify(ranked_videos.to_dict(orient="records"))

if __name__ == "__main__":
    app.run(debug=True)