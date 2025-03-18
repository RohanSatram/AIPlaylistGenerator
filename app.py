import os
from flask import Flask, render_template, request, redirect, url_for, session
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from google import genai
from google.genai.types import Tool, GenerateContentConfig, GoogleSearch
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Spotify API credentials
SPOTIFY_CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
SPOTIFY_CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')
SPOTIFY_REDIRECT_URI = 'http://localhost:5000/callback'

# Gemini API key
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

# Initialize Gemini client with Google Search
client = genai.Client(api_key=GEMINI_API_KEY)
model_id = "gemini-2.0-flash"
google_search_tool = Tool(google_search=GoogleSearch())

# Spotify OAuth setup
sp_oauth = SpotifyOAuth(
    client_id=SPOTIFY_CLIENT_ID,
    client_secret=SPOTIFY_CLIENT_SECRET,
    redirect_uri=SPOTIFY_REDIRECT_URI,
    scope='playlist-modify-public user-read-private user-read-email'
)

@app.route('/')
def index():
    if 'token_info' not in session:
        return render_template('index.html', logged_in=False)
    return render_template('index.html', logged_in=True)

@app.route('/login')
def login():
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)

@app.route('/callback')
def callback():
    code = request.args.get('code')
    token_info = sp_oauth.get_access_token(code)
    session['token_info'] = token_info
    return redirect(url_for('index'))

@app.route('/generate', methods=['POST'])
def generate_playlist():
    if 'token_info' not in session:
        return redirect(url_for('login'))
    
    preferences = request.form.get('preferences')
    
    # Get AI recommendations using Gemini with Google Search
    prompt = f"""Based on current music trends, recent releases, and the user's preferences, suggest 10 songs that would make a great playlist.
    User preferences: {preferences}
    
    Include current chart-topping songs and trending artists that match the user's preferences.
    Format the response as a JSON array of objects with 'title' and 'artist' fields.
    Example format:
    [
        {{"title": "Song Name", "artist": "Artist Name"}},
        ...
    ]
    """
    
    response = client.models.generate_content(
        model=model_id,
        contents=prompt,
        config=GenerateContentConfig(
            tools=[google_search_tool],
            response_modalities=["TEXT"],
        )
    )
    
    try:
        # Get the response text from the first candidate
        response_text = ""
        for part in response.candidates[0].content.parts:
            response_text += part.text
        
        # Find the JSON array in the response
        start_idx = response_text.find('[')
        end_idx = response_text.rfind(']') + 1
        json_str = response_text[start_idx:end_idx]
        songs = json.loads(json_str)
        
        # Store search suggestions in session for display
        session['search_suggestions'] = response.candidates[0].grounding_metadata.search_entry_point.rendered_content
        
    except Exception as e:
        print(f"Error parsing Gemini response: {e}")
        return "Error generating playlist. Please try again.", 500
    
    # Create Spotify playlist
    sp = spotipy.Spotify(auth=session['token_info']['access_token'])
    user_id = sp.current_user()['id']
    
    # Create new playlist
    playlist = sp.user_playlist_create(
        user_id,
        f"AI Generated Playlist - {preferences[:30]}",
        public=True
    )
    
    # Search and add songs
    for song in songs:
        results = sp.search(q=f"track:{song['title']} artist:{song['artist']}", type='track', limit=1)
        if results['tracks']['items']:
            track_uri = results['tracks']['items'][0]['uri']
            sp.playlist_add_items(playlist['id'], [track_uri])
    
    return redirect(playlist['external_urls']['spotify'])

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True) 