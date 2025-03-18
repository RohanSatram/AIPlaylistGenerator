# AI Spotify Playlist Generator

This project uses AI to generate personalized Spotify playlists based on your preferences. It combines Spotify's Web API with Google's Gemini AI to create unique playlists that match your taste in music.

## Features

- Generate playlists based on text descriptions of your mood or preferences
- AI-powered song recommendations using Google's Gemini with Google Search grounding
- Simple web interface
- Integration with your Spotify account

## Setup

1. Clone this repository
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Create a `.env` file in the root directory with the following variables:
   ```
   SPOTIFY_CLIENT_ID=your_spotify_client_id
   SPOTIFY_CLIENT_SECRET=your_spotify_client_secret
   GEMINI_API_KEY=your_gemini_api_key
   ```
4. Run the application:
   ```bash
   python app.py
   ```

## Getting Spotify Credentials

1. Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
2. Create a new application
3. Get your Client ID and Client Secret
4. Add `http://localhost:5000/callback` to your Redirect URIs in the Spotify Dashboard

## Getting Gemini API Key

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Copy the key to your `.env` file

## Usage

1. Start the application
2. Open your browser and go to `http://localhost:5000`
3. Log in with your Spotify account
4. Enter your preferences or mood in the text box
5. Click "Generate Playlist" to create a new playlist

## Testing

To test the Gemini integration separately:

```bash
python test.py
```
