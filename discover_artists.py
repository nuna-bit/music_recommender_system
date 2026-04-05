import os
import json
import pandas as pd
from datetime import timedelta
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import glob

# Try to use credentials from data_aquisition if it works
from data_aquisition import get_spotify_client

def load_data(data_path):
    all_files = glob.glob(os.path.join(data_path, "StreamingHistory_music_*.json.json"))
    dfs = []
    for f in all_files:
        with open(f, 'r', encoding='utf-8') as file:
            data = json.load(file)
            dfs.append(pd.DataFrame(data))
    
    df = pd.concat(dfs, ignore_index=True)
    df['endTime'] = pd.to_datetime(df['endTime'])
    return df

def get_top_artists_last_6_months(df, num_artists=10):
    # Find the most recent date in the dataset
    max_date = df['endTime'].max()
    six_months_ago = max_date - pd.DateOffset(months=6)
    
    # Filter last 6 months
    df_filtered = df[df['endTime'] >= six_months_ago]
    
    # Group by artist and sum msPlayed
    artist_playtime = df_filtered.groupby('artistName')['msPlayed'].sum().reset_index()
    
    # Sort by playtime
    artist_playtime = artist_playtime.sort_values(by='msPlayed', ascending=False)
    
    # Exclude "Unknown Artist"
    artist_playtime = artist_playtime[artist_playtime['artistName'] != "Unknown Artist"]
    
    return artist_playtime.head(num_artists)

def discover_new_artists(top_artists, all_historical_artists, sp):
    recommendations = {}
    
    for artist_name in top_artists['artistName']:
        result = sp.search(q=f"{artist_name} Radio", type="playlist", limit=5)
        if result and 'playlists' in result and result['playlists']['items']:
            playlist = next((p for p in result['playlists']['items'] if p is not None), None)
            if not playlist:
                continue
            playlist_id = playlist['id']
            
            try:
                tracks = sp.playlist_tracks(playlist_id, limit=30)
                for item in tracks['items']:
                    if not item:
                        continue
                    track = item.get('track')
                    if not track:
                        continue
                    
                    for artist in track['artists']:
                        rel_name = artist['name']
                        if rel_name not in all_historical_artists:
                            if rel_name not in recommendations:
                                recommendations[rel_name] = {
                                    'score': 0,
                                    'url': artist.get('external_urls', {}).get('spotify', ''),
                                    'id': artist['id'],
                                    'related_to': set()
                                }
                            recommendations[rel_name]['score'] += 1
                            recommendations[rel_name]['related_to'].add(artist_name)
            except Exception as e:
                print(f"Could not fetch playlist tracks for {artist_name}: {e}")
                
    # Sort and return
    rec_list = list(recommendations.values())
    for name, data in recommendations.items():
        data['name'] = name
        data['related_to'] = list(data['related_to'])
        
    rec_list.sort(key=lambda x: len(x['related_to']) + x['score'], reverse=True)
    
    top_recs = rec_list[:20]
    valid_ids = [r['id'] for r in top_recs if r.get('id')]
    if valid_ids:
        try:
            full_artists = sp.artists(valid_ids)
            for r, full_a in zip(top_recs, full_artists['artists']):
                if full_a:
                    r['popularity'] = full_a.get('popularity', 0)
                    r['genres'] = full_a.get('genres', [])
                else:
                    r['popularity'] = 0
                    r['genres'] = []
        except Exception as e:
            print(f"Could not fetch full artist details: {e}")
            for r in top_recs:
                r['popularity'] = 0
                r['genres'] = []
    return top_recs

def main():
    print("Loading data...")
    df = load_data('spotify_data')
    
    print("Finding top artists from the last 6 months...")
    top_artists = get_top_artists_last_6_months(df, num_artists=10)
    print("Top Artists:")
    for idx, row in top_artists.iterrows():
        print(f" - {row['artistName']} ({row['msPlayed'] / 60000:.1f} minutes)")
        
    all_historical_artists = set(df['artistName'].unique())
    
    sp = get_spotify_client()
    if not sp:
        print("Failed to initialize Spotify client.")
        return
        
    print("\nDiscovering new artists based on related artists...")
    recs = discover_new_artists(top_artists, all_historical_artists, sp)
    
    print("\n--- NEW ARTIST RECOMMENDATIONS ---")
    with open('artist_recommendations.md', 'w', encoding='utf-8') as f:
        f.write("# New Artist Recommendations\n\n")
        f.write("Based on your Spotify listening history from the past 6 months, here are some new artists you might like:\n\n")
        for i, rec in enumerate(recs, 1):
            genres = ", ".join(rec['genres'][:3]) if rec['genres'] else "Unknown genres"
            related = ", ".join(rec['related_to'])
            f.write(f"### {i}. {rec['name']} (Popularity: {rec['popularity']})\n")
            f.write(f"- **Genres**: {genres}\n")
            f.write(f"- **Because you like**: {related}\n")
            f.write(f"- **Listen**: [Spotify Link]({rec['url']})\n\n")
    print("Recommendations saved to artist_recommendations.md")

if __name__ == "__main__":
    main()
