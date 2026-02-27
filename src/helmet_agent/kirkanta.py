"""Kirkanta API client for library info and opening hours."""

from typing import Any

import httpx

BASE_URL = "https://api.kirjastot.fi/v4"


class KirkantaClient:
    """Async client for the Kirkanta library API."""

    def __init__(self, base_url: str = BASE_URL) -> None:
        self._base_url = base_url

    async def search_libraries(
        self,
        *,
        city: str = "helsinki",
        name: str | None = None,
        library_type: str = "municipal",
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        """Search for libraries by city and optional name.

        Returns a list of library dicts with keys: id, name, shortName, address, etc.
        """
        params: dict[str, str | int] = {
            "city.name": city,
            "type": library_type,
            "limit": limit,
        }
        if name:
            params["name"] = name

        async with httpx.AsyncClient() as http:
            resp = await http.get(f"{self._base_url}/library", params=params, timeout=30.0)
            resp.raise_for_status()
            data = resp.json()

        return data.get("items", [])

    async def get_schedules(
        self,
        library_id: int,
        *,
        period_start: str | None = None,
        period_end: str | None = None,
    ) -> dict[str, Any]:
        """Fetch library info with opening hour schedules.

        Returns a library dict including a 'schedules' list with daily entries.
        Each schedule entry has: date, closed, times (list of {from, to}), info.
        """
        params: dict[str, str] = {"with": "schedules"}
        if period_start:
            params["period.start"] = period_start
        if period_end:
            params["period.end"] = period_end

        async with httpx.AsyncClient() as http:
            resp = await http.get(
                f"{self._base_url}/library/{library_id}", params=params, timeout=30.0
            )
            resp.raise_for_status()
            data = resp.json()

        return data.get("data", {})
