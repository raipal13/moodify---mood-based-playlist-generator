import os
import urllib.parse
import requests
from dotenv import load_dotenv

from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import RedirectResponse

load_dotenv()

CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI")

if not CLIENT_ID or not CLIENT_SECRET or not REDIRECT_URI:
    raise RuntimeError("Missing Spotify environment variables")

SPOTIFY_AUTH_URL = "https://accounts.spotify.com/authorize"
SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"

router = APIRouter()


# -------------------------------------------------------------------
# LOGIN: Redirect user to Spotify consent screen
# -------------------------------------------------------------------
@router.get("/login")
def login():
    scope = "playlist-modify-private playlist-modify-public user-read-private user-top-read user-read-recently-played"

    params = {
        "client_id": CLIENT_ID,
        "response_type": "code",
        "redirect_uri": REDIRECT_URI,
        "scope": scope,
    }

    url = f"{SPOTIFY_AUTH_URL}?{urllib.parse.urlencode(params)}"
    return RedirectResponse(url)


# -------------------------------------------------------------------
# CALLBACK: Exchange code for tokens
# -------------------------------------------------------------------
@router.get("/callback")
def callback(request: Request):
    code = request.query_params.get("code")

    if not code:
        raise HTTPException(status_code=400, detail="Authorization code missing")

    payload = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
    }

    res = requests.post(SPOTIFY_TOKEN_URL, data=payload)

    if res.status_code != 200:
        raise HTTPException(
            status_code=500,
            detail=f"Token exchange failed: {res.text}",
        )

    token_data = res.json()

    return {
        "access_token": token_data.get("access_token"),
        "refresh_token": token_data.get("refresh_token"),
        "expires_in": token_data.get("expires_in"),
        "token_type": token_data.get("token_type"),
    }


# -------------------------------------------------------------------
# REFRESH TOKEN: Get a new access token
# (this is logic, not a public Spotify route)
# -------------------------------------------------------------------
def refresh_access_token(refresh_token: str):
    payload = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
    }

    res = requests.post(SPOTIFY_TOKEN_URL, data=payload)

    if res.status_code != 200:
        raise HTTPException(
            status_code=401,
            detail="Failed to refresh Spotify access token",
        )

    token_data = res.json()

    return {
        "access_token": token_data.get("access_token"),
        "expires_in": token_data.get("expires_in"),
        # Spotify may or may not return a new refresh_token
        "refresh_token": token_data.get("refresh_token", refresh_token),
    }
