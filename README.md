# Spotify Music Recommender

## Overview
The **Spotify Music Recommender System** is a personalized tool designed to help you discover new artists based on your actual listening habits. By analyzing your Spotify streaming history up to the **last 6 months**, the system identifies your top artists and utilizes curated music data to find exciting new recommendations that match your musical taste!

## How It Works
1. **Historical Data Parsing**: The project ingests your local Spotify GDPR data exports (`streaming_history.json` and `YourLibrary.json`) to understand what you're actively listening to.
2. **Top Artist Extraction**: It calculates the total play time for the artists you've listened to over the last 6 months to determine your true favorites.
3. **Spotify API Integration**: Utilizing the **Spotify Developer API** via `Spotipy`, the scripts fetch curated "Radio" playlists around your top artists. 
4. **Intelligent Filtering**: Because the goal is to discover *new* music, the recommendation engine rigorously filters out any artists that already exist anywhere within your historical streaming data.
5. **Ranking**: The final recommended artists are ranked based on their relevance to your top artists, and mapped with genres and Spotify links in a generated artifact.

## Setup Instructions
To run this project locally, ensure you have Python installed and the required dependencies:

```bash
pip install pandas spotipy
```

You must also set up your Spotify API credentials. You can set them as environment variables:
```bash
export SPOTIPY_CLIENT_ID='your_client_id_here'
export SPOTIPY_CLIENT_SECRET='your_client_secret_here'
```
*(Note: Windows users should use `set` or `$env:` in PowerShell).*

## Usage
Simply drop your Spotify Streaming History JSON files into the `/spotify_data` directory and run:

```bash
python discover_artists.py
```
This will automatically generate an `artist_recommendations.md` file featuring your new recommendations!

## License
This project is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for more information.
