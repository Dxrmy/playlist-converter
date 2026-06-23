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

def get_ytm_auth():
    import os
    headers_file = "headers_auth.json"
    if os.path.exists(headers_file):
        try:
            ytm = YTMusic(headers_file)
            ytm.get_library_playlists(limit=1)
            print("\nUsing existing YouTube Music login.")
            return ytm
        except Exception:
            print("\nExisting YouTube Music login expired or invalid. Please log in again.")
            
    print("\nTo upload to YouTube Music, you must provide request headers.")
    print("Please follow the instructions from ytmusicapi to get your headers:")
    print("Go to music.youtube.com, open Network tab, copy Request Headers as JSON.")
    try:
        from ytmusicapi import setup
        setup(filepath=headers_file)
        return YTMusic(headers_file)
    except Exception as e:
        print(f"Setup failed: {e}")
        return None

def ytm_to_spotify():
    urls = input("Enter YouTube Music playlist URL(s) separated by commas: ").split(",")
    
    print("\nLog in to Spotify to create playlist(s):")
    email = input("Spotify Email: ")
    password = input("Spotify Password: ")
    cfg = Config(logger=NoopLogger())
    instance = Login(cfg, password, email=email)
    print("Logging into Spotify...")
    instance.login()
    
    priv_pl = PrivatePlaylist(instance)
    song_api = Song(priv_pl)
    ytm = YTMusic()
    
    for url in urls:
        url = url.strip()
        if not url: continue
        pl_id = get_ytm_playlist_id(url)
        print(f"\nFetching YT Music playlist...")
        try:
            pl = ytm.get_playlist(pl_id)
        except Exception as e:
            print(f"Failed to fetch YTM playlist: {e}")
            continue
            
        print(f"Found YT Music playlist: {pl['title']}")
        
        new_uri = priv_pl.create_playlist(f"{pl['title']} (from YTM)")
        priv_pl.set_playlist(new_uri)
        
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
            print(f"\nCompleted {pl['title']}! However, {len(failed_tracks)} tracks could not be found/added:")
            for t in failed_tracks:
                print(f"  - {t}")
        else:
            print(f"\nCompleted {pl['title']}! All tracks were successfully added.")

def spotify_to_ytm():
    urls = input("Enter Spotify playlist URL(s) separated by commas: ").split(",")
    ytm_auth = get_ytm_auth()
    if not ytm_auth: return
    
    for url in urls:
        url = url.strip()
        if not url: continue
        pl_id = get_spotify_playlist_id(url)
        print(f"\nFetching Spotify playlist...")
        try:
            pl = PublicPlaylist(pl_id)
            info = pl.get_playlist_info()
        except Exception as e:
            print(f"Failed to fetch Spotify playlist: {e}")
            continue
            
        pl_data = info.get("data", {}).get("playlistV2", {})
        title = pl_data.get("name", "Spotify Playlist")
        owner = pl_data.get("ownerV2", {}).get("data", {}).get("name", "")
        if owner:
            title = f"{title} - {owner}"
        print(f"Found Spotify playlist: {title}")
        
        tracks = []
        for batch in pl.paginate_playlist():
            for item in batch.get("items", []):
                track = item.get("itemV2", {}).get("data", {})
                if track:
                    t_name = track.get("name", "")
                    t_artists = " ".join([a.get("profile", {}).get("name", "") for a in track.get("artists", {}).get("items", [])])
                    tracks.append(f"{t_name} {t_artists}")
                    
        print(f"Found {len(tracks)} tracks.")
        
        desc = f"Imported from Spotify account {owner} (https://github.com/Dxrmy/playlist-converter)" if owner else "Imported from Spotify (https://github.com/Dxrmy/playlist-converter)"
        new_pl_id = ytm_auth.create_playlist(title, desc)
        failed_tracks = []
        for query in tracks:
            print(f"Searching YT Music for: {query}")
            try:
                results = ytm_auth.search(query, filter="songs", limit=1)
                if results:
                    vid = results[0]['videoId']
                    ytm_auth.add_playlist_items(new_pl_id, [vid], duplicates=True)
                    print(f" -> Added {query}")
                else:
                    print(f" -> Could not find {query}")
                    failed_tracks.append(query)
            except Exception as e:
                print(f" -> Error adding {query}: {e}")
                failed_tracks.append(query)

        if failed_tracks:
            print(f"\nCompleted {title}! However, {len(failed_tracks)} tracks could not be found/added:")
            for t in failed_tracks:
                print(f"  - {t}")
        else:
            print(f"\nCompleted {title}! All tracks were successfully added.")

if __name__ == '__main__':
    while True:
        print("\n=== Playlist Converter ===")
        print("1. YouTube Music to Spotify")
        print("2. Spotify to YouTube Music")
        print("3. Exit")
        choice = input("Select (1/2/3): ")
        if choice == '1':
            ytm_to_spotify()
        elif choice == '2':
            spotify_to_ytm()
        elif choice == '3':
            break
        else:
            print("Invalid choice.")
