# Universal Playlist Converter

Seamlessly convert and transfer your playlists between YouTube Music and Spotify, and vice versa. 

Works cleanly using unofficial APIs, meaning you do not need to register a Spotify Developer App or configure complex OAuth flows. You only need to log in to the service you are transferring *to*.

## Usage

### Windows
Open **PowerShell** and run the following command:
```powershell
irm https://raw.githubusercontent.com/Dxrmy/playlist-converter/main/run.ps1 | iex
```

### macOS & Linux
Open your **Terminal** and run the following command:
```bash
curl -sL https://raw.githubusercontent.com/Dxrmy/playlist-converter/main/run.sh | bash
```

## What this does
1. Detects if Python is installed on your system
2. Sets up a temporary virtual environment (`.venv`) to keep your system clean
3. Installs the required API libraries (`spotapi` and `ytmusicapi`)
4. Runs the converter script which interacts natively with Spotify and YouTube Music's web APIs
5. Allows you to fetch playlists publicly and securely log in with email/password or browser cookies to transfer your songs
