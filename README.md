YouTubeVideoAnalyzer/
├── app/                                 # Main application folder
│   ├── __init__.py                      # Initializes the Flask app
│   ├── routes.py                        # Defines routes for handling requests
│   ├── youtube_analyzer.py              # YouTube data processing functions
│   ├── static/                          # Static files (CSS, JavaScript, images)
│   │   ├── css/
│   │   │   └── styles.css               # CSS for styling the UI
│   │   ├── js/
│   │   │   └── script.js                # JavaScript for frontend interactions
│   │   └── images/                      # Folder for any images or icons
│   ├── templates/                       # HTML templates
│   │   ├── layout.html                  # Base HTML layout (header, footer, etc.)
│   │   └── index.html                   # Main HTML template for the UI
│   ├── utils/                           # Utility functions
│   │   └── helpers.py                   # Helper functions for data processing
│   ├── tests/                           # Tests for the backend
│   │   └── test_youtube_analyzer.py     # Unit tests for YouTube analyzer functions
│   ├── config.py                        # Configuration settings for the Flask app
│   └── credentials.json                 # YouTube API credentials (add to .gitignore)
│
├── .gitignore                           # Specifies files and folders to ignore in Git
├── requirements.txt                     # Python dependencies
├── README.md                            # Main project documentation
└── run.py                               # Entry point to run the Flask app
