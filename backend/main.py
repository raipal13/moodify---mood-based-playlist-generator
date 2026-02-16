from fastapi import FastAPI, APIRouter
from backend.auth import router as auth_router
from backend.clients.spotify_client import SpotifyClient
from backend.mood import generate_tracks_for_mood

app = FastAPI()
router = APIRouter()

app.include_router(auth_router)


@router.post("/generate-playlist")
async def generate_playlist(mood: str, access_token: str):

    client = SpotifyClient(access_token)

    # 1️⃣ Get current user
    user = await client.get_current_user()
    user_id = user["id"]

    # 2️⃣ Generate track URIs
    uris = await generate_tracks_for_mood(access_token, mood)
    print("Generated URIs:", uris[:5])

    if not uris:
        return {
            "tracks_added": 0,
            "warning": "No tracks found for this mood."
        }

    # 3️⃣ Create playlist
    playlist = await client.create_playlist(
        user_id=user_id,
        name=f"Moodify – {mood.capitalize()}",
        description=f"{mood.capitalize()} mood playlist",
    )

    playlist_id = playlist["id"]

    # 4️⃣ Add tracks
    await client.add_tracks(playlist_id, uris)

    # 5️⃣ Respond
    return {
        "playlist_url": playlist["external_urls"]["spotify"],
        "tracks_added": len(uris),
    }


app.include_router(router)
