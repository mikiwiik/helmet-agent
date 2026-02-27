"""Finna REST API client for searching Helmet library materials."""

from typing import Any

import httpx

BASE_URL = "https://api.finna.fi/v1"

DEFAULT_FIELDS = ["id", "title", "authors", "formats", "buildings", "year"]


class FinnaClient:
    """Async client for the Finna REST API."""

    def __init__(self, base_url: str = BASE_URL) -> None:
        self._base_url = base_url

    async def search(
        self,
        query: str,
        *,
        search_type: str = "AllFields",
        filters: list[str] | None = None,
        fields: list[str] | None = None,
        limit: int = 20,
        page: int = 1,
    ) -> dict[str, Any]:
        """Search for materials in the Finna catalog.

        Returns the raw API response dict with keys: resultCount, records, status.
        """
        params: list[tuple[str, str]] = [
            ("lookfor", query),
            ("type", search_type),
            ("limit", str(limit)),
            ("page", str(page)),
        ]
        for field in fields or DEFAULT_FIELDS:
            params.append(("field[]", field))
        for f in filters or []:
            params.append(("filter[]", f))

        async with httpx.AsyncClient() as http:
            resp = await http.get(f"{self._base_url}/search", params=params, timeout=30.0)
            resp.raise_for_status()
            return resp.json()

    async def get_record(
        self,
        record_id: str,
        *,
        fields: list[str] | None = None,
    ) -> dict[str, Any]:
        """Fetch a single record by ID.

        Returns the record dict. Raises ValueError if not found.
        """
        params: list[tuple[str, str]] = [("id", record_id)]
        for field in fields or DEFAULT_FIELDS:
            params.append(("field[]", field))

        async with httpx.AsyncClient() as http:
            resp = await http.get(f"{self._base_url}/record", params=params, timeout=30.0)
            resp.raise_for_status()
            data = resp.json()

        if not data.get("records"):
            raise ValueError(f"Record {record_id!r} not found")
        return data["records"][0]

    async def get_building_facets(
        self,
        *,
        parent: str | None = None,
    ) -> list[dict[str, Any]]:
        """Fetch building facet values for Helmet libraries.

        If parent is given (e.g. '1/Helmet/h/'), filters to that building first.
        Returns a list of facet dicts with keys: value, translated, count.
        """
        params: list[tuple[str, str]] = [
            ("lookfor", ""),
            ("limit", "0"),
            ("facet[]", "building"),
        ]
        if parent:
            params.append(("filter[]", f'building:"{parent}"'))
        else:
            params.append(("filter[]", 'building:"0/Helmet/"'))

        async with httpx.AsyncClient() as http:
            resp = await http.get(f"{self._base_url}/search", params=params, timeout=30.0)
            resp.raise_for_status()
            data = resp.json()

        return data.get("facets", {}).get("building", [])
