import httpx

BASE_URL = "https://api.spotify.com/v1"


class SpotifyClient:
    def __init__(self, access_token: str):
        self.headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }

    async def _request(self, method: str, endpoint: str, **kwargs):
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.request(
                method,
                f"{BASE_URL}{endpoint}",
                headers=self.headers,
                **kwargs,
            )

        response.raise_for_status()
        return response.json()

    async def get_current_user(self):
        return await self._request("GET", "/me")

    async def search_tracks(self, query: str, limit: int = 20):
        return await self._request(
            "GET",
            "/search",
            params={
                "q": query,
                "type": "track",
                "limit": limit,
            },
        )

    async def create_playlist(self, user_id: str, name: str, description: str):
        return await self._request(
            "POST",
            f"/users/{user_id}/playlists",
            json={
                "name": name,
                "description": description,
                "public": False,
            },
        )

    async def add_tracks(self, playlist_id: str, uris: list[str]):
        return await self._request(
            "POST",
            f"/playlists/{playlist_id}/tracks",
            json={"uris": uris},
        )
    async def get_top_artists(self, limit: int = 10):
        return await self._request(
            "GET",
            "/me/top/artists",
            params={"limit": limit},
    )
