import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth

# Safe, writable location for Windows
CACHE_PATH = os.path.join(os.path.expanduser("~"), ".spotipy_token_cache")

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id="00f2556693ce46f1b7c2e12c38e1521d",
    client_secret="72253db324594a1587ea4858f32772d4",
    redirect_uri="http://127.0.0.1:8000/callback",
    scope="user-modify-playback-state,user-read-playback-state",
    cache_path=CACHE_PATH
))

def play_pause_toggle():
    state = sp.current_playback()
    if state and state.get("is_playing"):
        print(">>> PAUSE")
        sp.pause_playback()
    else:
        print(">>> PLAY")
        sp.start_playback()

def skip_track():
    print(">>> SKIP TRACK")
    sp.next_track()

def volume_control(value):
    sp.volume(value)