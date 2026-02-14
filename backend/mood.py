import requests
from backend.spotify_client import get_top_artists

MOOD_QUERIES = {
    "happy": ["happy pop", "feel good pop"],
    "sad": ["sad acoustic", "heartbreak songs"],
    "calm": ["chill acoustic", "lofi chill"],
    "energetic": ["workout dance", "high energy edm"],
}

SPOTIFY_SEARCH_URL = "https://api.spotify.com/v1/search"


def search_tracks(access_token: str, query: str, limit: int = 20):
    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    params = {
        "q": query,
        "type": "track",
        "limit": limit
    }

    res = requests.get(SPOTIFY_SEARCH_URL, headers=headers, params=params)
    res.raise_for_status()

    return res.json()["tracks"]["items"]


def generate_tracks_for_mood(access_token: str, mood: str, max_tracks: int = 30):

    queries = MOOD_QUERIES.get(mood, ["pop"])
    uris = []
    seen = set()

    # 1️⃣ Base mood tracks
    for q in queries:
        tracks = search_tracks(access_token, q)
        for track in tracks:
            uri = track["uri"]
            if uri not in seen:
                seen.add(uri)
                uris.append(uri)

    # 2️⃣ Personalization boost
    try:
        top_artists = get_top_artists(access_token)

        for artist in top_artists:
            artist_query = f"{artist['name']} {mood}"
            tracks = search_tracks(access_token, artist_query, limit=5)

            for track in tracks:
                uri = track["uri"]
                if uri not in seen:
                    seen.add(uri)
                    uris.insert(0, uri)  # boost
    except Exception:
        pass  # personalization optional

    return uris[:max_tracks]
