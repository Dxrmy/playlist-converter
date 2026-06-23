import sys
import re
from ytmusicapi import YTMusic
from spotapi import Login, Config, NoopLogger, PrivatePlaylist, Song, PublicPlaylist
from rich.progress import Progress, TextColumn, BarColumn, TaskProgressColumn
from rich.console import Console

console = Console()

def get_ytm_playlist_id(url):
    match = re.search(r'list=([a-zA-Z0-9_-]+)', url)
    if match: return match.group(1)
    return None

def get_spotify_playlist_id(url):
    match = re.search(r'playlist/([a-zA-Z0-9]+)', url)
    if match: return match.group(1)
    return None

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
        if not pl_id:
            print(f"\nSkipping invalid YouTube Music playlist URL: {url}")
            continue
            
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
        with Progress(
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=console
        ) as progress:
            bar_task = progress.add_task(f"[green]Converting {pl['title']}...", total=len(pl['tracks']))
            status_task = progress.add_task("[cyan]Starting...", total=None)
            
            for track in pl['tracks']:
                title = track['title']
                artists = " ".join([a['name'] for a in track['artists']]) if track['artists'] else ""
                query = f"{title} {artists}"
                progress.update(status_task, description=f"[cyan]Searching: {query}")
                try:
                    res = song_api.query_songs(query, limit=1)
                    items = res.get("data", {}).get("searchV2", {}).get("tracksV2", {}).get("items", [])
                    if items:
                        track_id = items[0]["item"]["data"]["id"]
                        song_api.add_song_to_playlist(track_id)
                    else:
                        failed_tracks.append(title)
                except Exception:
                    failed_tracks.append(title)
                progress.advance(bar_task)
            progress.remove_task(status_task)

        if failed_tracks:
            console.print(f"\n[yellow]Completed {pl['title']}! However, {len(failed_tracks)} tracks could not be found/added:[/yellow]")
            for t in failed_tracks:
                console.print(f"  - {t}")
        else:
            console.print(f"\n[green]Completed {pl['title']}! All tracks were successfully added.[/green]")

def spotify_to_ytm():
    urls = input("Enter Spotify playlist URL(s) separated by commas: ").split(",")
    ytm_auth = get_ytm_auth()
    if not ytm_auth: return
    
    for url in urls:
        url = url.strip()
        if not url: continue
        pl_id = get_spotify_playlist_id(url)
        if not pl_id:
            print(f"\nSkipping invalid Spotify playlist URL: {url}")
            continue
            
        print(f"\nFetching Spotify playlist...")
        try:
            pl = PublicPlaylist(pl_id)
            info = pl.get_playlist_info()
        except Exception as e:
            print(f"Failed to fetch Spotify playlist: {e}")
            continue
            
        pl_data = info.get("data", {}).get("playlistV2", {})
        title = pl_data.get("name", "Spotify Playlist")
        print(f"Found Spotify playlist: {title}")
        
        tracks = []
        try:
            for batch in pl.paginate_playlist():
                for item in batch.get("items", []):
                    track = item.get("itemV2", {}).get("data", {})
                    if track:
                        t_name = track.get("name", "")
                        t_artists = " ".join([a.get("profile", {}).get("name", "") for a in track.get("artists", {}).get("items", [])])
                        tracks.append(f"{t_name} {t_artists}")
        except Exception as e:
            print(f"Failed to extract tracks (is this a valid Spotify playlist URL?): {e}")
            continue
                    
        print(f"Found {len(tracks)} tracks.")
        
        desc = "https://github.com/Dxrmy/playlist-converter"
        new_pl_id = ytm_auth.create_playlist(title, desc)
        failed_tracks = []
        with Progress(
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=console
        ) as progress:
            bar_task = progress.add_task(f"[green]Converting {title}...", total=len(tracks))
            status_task = progress.add_task("[cyan]Starting...", total=None)
            
            for query in tracks:
                progress.update(status_task, description=f"[cyan]Searching: {query}")
                try:
                    results = ytm_auth.search(query, filter="songs", limit=1)
                    if results:
                        vid = results[0]['videoId']
                        ytm_auth.add_playlist_items(new_pl_id, [vid], duplicates=True)
                    else:
                        failed_tracks.append(query)
                except Exception:
                    failed_tracks.append(query)
                progress.advance(bar_task)
            progress.remove_task(status_task)

        if failed_tracks:
            console.print(f"\n[yellow]Completed {title}! However, {len(failed_tracks)} tracks could not be found/added:[/yellow]")
            for t in failed_tracks:
                console.print(f"  - {t}")
        else:
            console.print(f"\n[green]Completed {title}! All tracks were successfully added.[/green]")

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
