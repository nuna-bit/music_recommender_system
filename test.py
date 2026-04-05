from data_aquisition import get_spotify_client
try:
    sp = get_spotify_client()
    result = sp.search(q="Coldplay Radio", type="playlist", limit=5)
    if result and 'playlists' in result and result['playlists']['items']:
        # Find the first valid playlist
        playlist = next((p for p in result['playlists']['items'] if p is not None), None)
        if playlist:
            playlist_id = playlist['id']
            tracks = sp.playlist_tracks(playlist_id, limit=10)
            found_artists = []
            for item in tracks['items']:
                track = item.get('track')
                if track:
                    for artist in track['artists']:
                        found_artists.append(artist['name'])
            print("Found artists:", found_artists)
        else:
            print("No valid playlists found.")
except Exception as e:
    import traceback
    traceback.print_exc()
