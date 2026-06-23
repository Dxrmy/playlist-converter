import sys
import re
from ytmusicapi import YTMusic
from spotapi import Login, Config, NoopLogger, PrivatePlaylist, Song, PublicPlaylist

def get_ytm_playlist_id(url):
    match = re.search(r'list=([a-zA-Z0-9_-]+)', url)
    if match: return match.group(1)
    return url

def get_spotify_playlist_id(url):
    match = re.search(r'playlist/([a-zA-Z0-9]+)', url)
    if match: return match.group(1)
    return url

def ytm_to_spotify():
    url = input("Enter YouTube Music playlist URL: ")
    pl_id = get_ytm_playlist_id(url)
    print("\nFetching YT Music playlist...")
    ytm = YTMusic()
    pl = ytm.get_playlist(pl_id)
    print(f"Found YT Music playlist: {pl['title']}")
    
    print("\nLog in to Spotify to create playlist:")
    email = input("Spotify Email: ")
    password = input("Spotify Password: ")
    cfg = Config(logger=NoopLogger())
    instance = Login(cfg, password, email=email)
    print("Logging into Spotify...")
    instance.login()
    
    priv_pl = PrivatePlaylist(instance)
    new_uri = priv_pl.create_playlist(f"{pl['title']} (from YTM)")
    priv_pl.set_playlist(new_uri)
    song_api = Song(priv_pl)
    
    failed_tracks = []
    for track in pl['tracks']:
        title = track['title']
        artists = " ".join([a['name'] for a in track['artists']]) if track['artists'] else ""
        query = f"{title} {artists}"
        print(f"Searching Spotify for: {query}")
        try:
            res = song_api.query_songs(query, limit=1)
            items = res.get("data", {}).get("searchV2", {}).get("tracksV2", {}).get("items", [])
            if items:
                track_id = items[0]["item"]["data"]["id"]
                song_api.add_song_to_playlist(track_id)
                print(f" -> Added {title}")
            else:
                print(f" -> Could not find {title}")
                failed_tracks.append(title)
        except Exception as e:
            print(f" -> Failed to add {title}: {e}")
            failed_tracks.append(title)

    if failed_tracks:
        print(f"\nCompleted! However, {len(failed_tracks)} tracks could not be found/added:")
        for t in failed_tracks:
            print(f"  - {t}")
    else:
        print("\nCompleted! All tracks were successfully added.")

def spotify_to_ytm():
    url = input("Enter Spotify playlist URL: ")
    pl_id = get_spotify_playlist_id(url)
    print("\nFetching Spotify playlist...")
    pl = PublicPlaylist(pl_id)
    info = pl.get_playlist_info()
    pl_data = info.get("data", {}).get("playlistV2", {})
    title = pl_data.get("name", "Spotify Playlist")
    owner = pl_data.get("ownerV2", {}).get("data", {}).get("name", "")
    if owner:
        title = f"{title} - {owner}"
    print(f"Found Spotify playlist: {title}")
    
    # Get all tracks
    tracks = []
    for batch in pl.paginate_playlist():
        for item in batch.get("items", []):
            track = item.get("itemV2", {}).get("data", {})
            if track:
                t_name = track.get("name", "")
                t_artists = " ".join([a.get("profile", {}).get("name", "") for a in track.get("artists", {}).get("items", [])])
                tracks.append(f"{t_name} {t_artists}")
                
    print(f"Found {len(tracks)} tracks.")
    
    print("\nTo upload to YouTube Music, you must provide request headers.")
    print("Please follow the instructions from ytmusicapi to get your headers:")
    print("Go to music.youtube.com, open Network tab, copy Request Headers as JSON.")
    headers_file = "headers_auth.json"
    ytm = YTMusic()
    try:
        from ytmusicapi import setup
        setup(filepath=headers_file)
        ytm_auth = YTMusic(headers_file)
    except Exception as e:
        print(f"Setup failed: {e}")
        return
        
    desc = f"Imported from Spotify account {owner} (https://github.com/Dxrmy/playlist-converter)" if owner else "Imported from Spotify (https://github.com/Dxrmy/playlist-converter)"
    pl_id = ytm_auth.create_playlist(title, desc)
    failed_tracks = []
    for query in tracks:
        print(f"Searching YT Music for: {query}")
        try:
            results = ytm_auth.search(query, filter="songs", limit=1)
            if results:
                vid = results[0]['videoId']
                ytm_auth.add_playlist_items(pl_id, [vid], duplicates=True)
                print(f" -> Added {query}")
            else:
                print(f" -> Could not find {query}")
                failed_tracks.append(query)
        except Exception as e:
            print(f" -> Error adding {query}: {e}")
            failed_tracks.append(query)

    if failed_tracks:
        print(f"\nCompleted! However, {len(failed_tracks)} tracks could not be found/added:")
        for t in failed_tracks:
            print(f"  - {t}")
    else:
        print("\nCompleted! All tracks were successfully added.")

if __name__ == '__main__':
    print("=== Playlist Converter ===")
    print("1. YouTube Music to Spotify")
    print("2. Spotify to YouTube Music")
    choice = input("Select (1/2): ")
    if choice == '1':
        ytm_to_spotify()
    elif choice == '2':
        spotify_to_ytm()
    else:
        print("Invalid choice.")
