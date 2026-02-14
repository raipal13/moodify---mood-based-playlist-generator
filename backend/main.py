from fastapi import FastAPI, APIRouter
from backend.auth import router as auth_router
from backend.mood import generate_tracks_for_mood
from backend.spotify_client import create_playlist, add_tracks_to_playlist

app = FastAPI()
router = APIRouter()

app.include_router(auth_router)

@router.post("/generate-playlist")
def generate_playlist(mood: str, access_token: str):
    
    from backend.spotify_client import get_current_user_id

    user_id = get_current_user_id(access_token)


    # 1️⃣ Generate track URIs
    uris = generate_tracks_for_mood(access_token, mood)
    print("Generated URIs:", uris[:5])

    if not uris:
        return {
            "tracks_added": 0,
            "warning": "No tracks found for this mood."
        }

    # 2️⃣ Create playlist
    playlist = create_playlist(
        user_id=user_id,
        token=access_token,
        name=f"Moodify – {mood.capitalize()}",
        description=f"{mood.capitalize()} mood playlist"
    )

    playlist_id = playlist["id"]

    # 3️⃣ Add tracks
    add_tracks_to_playlist(
        playlist_id=playlist_id,
        uris=uris,
        token=access_token
    )

    # 4️⃣ Respond
    return {
        "playlist_url": playlist["external_urls"]["spotify"],
        "tracks_added": len(uris)
    }

app.include_router(router)
