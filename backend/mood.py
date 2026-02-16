from backend.clients.spotify_client import SpotifyClient

MOOD_QUERIES = {
    "happy": ["happy pop", "feel good pop"],
    "sad": ["sad acoustic", "heartbreak songs"],
    "calm": ["chill acoustic", "lofi chill"],
    "energetic": ["workout dance", "high energy edm"],
}


async def generate_tracks_for_mood(
    access_token: str,
    mood: str,
    max_tracks: int = 30,
):
    client = SpotifyClient(access_token)

    queries = MOOD_QUERIES.get(mood, ["pop"])
    uris = []
    seen = set()

    # 1️⃣ Base mood tracks
    for q in queries:
        data = await client.search_tracks(q)
        tracks = data["tracks"]["items"]

        for track in tracks:
            uri = track["uri"]
            if uri not in seen:
                seen.add(uri)
                uris.append(uri)

    # 2️⃣ Personalization boost
    try:
        top_data = await client.get_top_artists()
        top_artists = top_data["items"]

        for artist in top_artists:
            artist_query = f"{artist['name']} {mood}"
            data = await client.search_tracks(artist_query, limit=5)
            tracks = data["tracks"]["items"]

            for track in tracks:
                uri = track["uri"]
                if uri not in seen:
                    seen.add(uri)
                    uris.insert(0, uri)

    except Exception:
        pass  # personalization optional

    return uris[:max_tracks]
