import requests

SPOTIFY_BASE_URL = "https://api.spotify.com/v1"

def get_top_artists(token: str, limit: int = 10):
    url = "https://api.spotify.com/v1/me/top/artists"
    res = requests.get(
        url,
        headers=get_headers(token),
        params={"limit": limit}
    )
    res.raise_for_status()
    return res.json()["items"]

def get_current_user_id(token: str):
    url = "https://api.spotify.com/v1/me"
    res = requests.get(url, headers=get_headers(token))
    res.raise_for_status()
    return res.json()["id"]

def get_headers(token: str):
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

def create_playlist(user_id: str, token: str, name: str, description: str):
    url = f"{SPOTIFY_BASE_URL}/users/{user_id}/playlists"
    payload = {
        "name": name,
        "description": description,
        "public": False
    }

    res = requests.post(url, headers=get_headers(token), json=payload)
    res.raise_for_status()
    return res.json()

def add_tracks_to_playlist(playlist_id: str, uris: list[str], token: str):
    url = f"{SPOTIFY_BASE_URL}/playlists/{playlist_id}/tracks"

    for i in range(0, len(uris), 100):
        batch = uris[i:i+100]
        res = requests.post(
            url,
            headers=get_headers(token),
            json={"uris": batch}
        )
        res.raise_for_status()
