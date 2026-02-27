"""Integration tests for MCP tool functions."""

import httpx
import respx

from helmet_agent.server import mcp
from helmet_agent import tools


FINNA_URL = "https://api.finna.fi/v1"
KIRKANTA_URL = "https://api.kirjastot.fi/v4"

# Sample building facets returned by Finna
SAMPLE_FACETS = [
    {"value": "0/Helmet/", "translated": "Helmet-kirjastot", "count": 795567},
    {"value": "1/Helmet/h/", "translated": "Helsinki", "count": 400000},
    {"value": "1/Helmet/e/", "translated": "Espoo", "count": 200000},
    {"value": "1/Helmet/v/", "translated": "Vantaa", "count": 150000},
    {"value": "1/Helmet/k/", "translated": "Kauniainen", "count": 30000},
    {"value": "2/Helmet/h/h01/", "translated": "Pasila", "count": 50000},
    {"value": "2/Helmet/h/h55/", "translated": "Munkkiniemi", "count": 20000},
    {"value": "2/Helmet/h/h82/", "translated": "Roihuvuori", "count": 15000},
    {"value": "2/Helmet/v/v30/", "translated": "Tikkurila", "count": 22000},
]


def test_server_has_name():
    assert mcp.name == "helmet-library"


class TestSearchMaterials:
    @respx.mock
    async def test_search_by_author_and_branch(self):
        # Mock facet fetch for branch resolver init
        respx.get(f"{FINNA_URL}/search").mock(
            side_effect=_finna_router,
        )

        tools._branch_resolver = None  # reset state

        result = await tools.search_materials(query="väinö linna", author="väinö linna", branch="Munkkiniemi")

        assert "Tuntematon sotilas" in result
        assert "helmet.2280900" in result
        assert "Munkkiniemi" in result or "Pasila" in result

    @respx.mock
    async def test_search_no_results(self):
        respx.get(f"{FINNA_URL}/search").mock(
            side_effect=_finna_router,
        )

        tools._branch_resolver = None

        result = await tools.search_materials(query="xyznonexistent999")

        assert "No results" in result or "no results" in result

    @respx.mock
    async def test_search_with_format_filter(self):
        respx.get(f"{FINNA_URL}/search").mock(
            side_effect=_finna_router,
        )

        tools._branch_resolver = None

        result = await tools.search_materials(query="sinuhe", material_format="Book")

        assert isinstance(result, str)

    @respx.mock
    async def test_search_without_branch(self):
        respx.get(f"{FINNA_URL}/search").mock(
            side_effect=_finna_router,
        )

        tools._branch_resolver = None

        result = await tools.search_materials(query="tuntematon sotilas")

        assert "Tuntematon sotilas" in result


class TestGetRecordDetail:
    @respx.mock
    async def test_get_record(self):
        respx.get(f"{FINNA_URL}/record").mock(
            return_value=httpx.Response(200, json={
                "resultCount": 1,
                "records": [{
                    "id": "helmet.2280900",
                    "title": "Tuntematon sotilas",
                    "year": "2017",
                    "authors": {
                        "primary": {"Linna, Väinö": {"role": ["kirjoittaja"]}},
                        "secondary": [],
                        "corporate": [],
                    },
                    "formats": [{"value": "0/Book/", "translated": "Kirja"}],
                    "buildings": [
                        {"value": "2/Helmet/h/h01/", "translated": "Pasila"},
                        {"value": "2/Helmet/h/h82/", "translated": "Roihuvuori"},
                    ],
                }],
                "status": "OK",
            })
        )

        result = await tools.get_record_detail(record_id="helmet.2280900")

        assert "Tuntematon sotilas" in result
        assert "Linna" in result
        assert "Pasila" in result
        assert "helmet.finna.fi" in result

    @respx.mock
    async def test_get_record_not_found(self):
        respx.get(f"{FINNA_URL}/record").mock(
            return_value=httpx.Response(200, json={
                "resultCount": 0,
                "records": [],
                "status": "OK",
            })
        )

        result = await tools.get_record_detail(record_id="helmet.nonexistent")

        assert "not found" in result.lower() or "error" in result.lower()


class TestListLibraryBranches:
    @respx.mock
    async def test_list_branches(self):
        respx.get(f"{FINNA_URL}/search").mock(
            return_value=httpx.Response(200, json={
                "resultCount": 0,
                "facets": {"building": SAMPLE_FACETS},
                "status": "OK",
            })
        )

        tools._branch_resolver = None

        result = await tools.list_library_branches(city="Helsinki")

        assert "Pasila" in result
        assert "Munkkiniemi" in result
        assert "Roihuvuori" in result


class TestGetOpeningHours:
    @respx.mock
    async def test_get_opening_hours(self):
        respx.get(f"{KIRKANTA_URL}/library").mock(
            return_value=httpx.Response(200, json={
                "type": "library",
                "total": 1,
                "items": [{
                    "id": 84867,
                    "name": "Munkkiniemen kirjasto",
                    "shortName": "Munkkiniemi",
                    "type": "municipal",
                    "address": {
                        "street": "Riihitie 22",
                        "city": "Helsinki",
                        "zipcode": "00330",
                    },
                }],
            })
        )
        respx.get(f"{KIRKANTA_URL}/library/84867").mock(
            return_value=httpx.Response(200, json={
                "type": "library",
                "total": 1,
                "data": {
                    "id": 84867,
                    "name": "Munkkiniemen kirjasto",
                    "shortName": "Munkkiniemi",
                    "address": {
                        "street": "Riihitie 22",
                        "city": "Helsinki",
                        "zipcode": "00330",
                    },
                    "schedules": [
                        {
                            "date": "2026-02-27",
                            "closed": False,
                            "times": [{"from": "09:00", "to": "16:00", "status": 1}],
                        },
                        {
                            "date": "2026-02-28",
                            "closed": False,
                            "times": [{"from": "10:00", "to": "16:00", "status": 1}],
                        },
                    ],
                },
            })
        )

        result = await tools.get_opening_hours(library_name="Munkkiniemi")

        assert "Munkkiniemen kirjasto" in result
        assert "09:00" in result
        assert "16:00" in result
        assert "Riihitie" in result

    @respx.mock
    async def test_get_opening_hours_not_found(self):
        respx.get(f"{KIRKANTA_URL}/library").mock(
            return_value=httpx.Response(200, json={
                "type": "library",
                "total": 0,
                "items": [],
            })
        )

        result = await tools.get_opening_hours(library_name="nonexistent")

        assert "not found" in result.lower() or "no library" in result.lower()


def _finna_router(request: httpx.Request) -> httpx.Response:
    """Route Finna API mocks based on request params."""
    url = str(request.url)

    # Facet request (for branch resolver init)
    if "facet" in url and "building" in url:
        return httpx.Response(200, json={
            "resultCount": 0,
            "facets": {"building": SAMPLE_FACETS},
            "status": "OK",
        })

    # Search with nonsense query
    if "xyznonexistent999" in url:
        return httpx.Response(200, json={
            "resultCount": 0,
            "records": [],
            "status": "OK",
        })

    # Default search response
    return httpx.Response(200, json={
        "resultCount": 2,
        "records": [
            {
                "id": "helmet.2280900",
                "title": "Tuntematon sotilas",
                "year": "2017",
                "formats": [{"value": "0/Book/", "translated": "Kirja"}],
                "buildings": [
                    {"value": "0/Helmet/", "translated": "Helmet-kirjastot"},
                    {"value": "2/Helmet/h/h01/", "translated": "Pasila"},
                ],
                "authors": {
                    "primary": {"Linna, Väinö": {"role": ["kirjoittaja"]}},
                    "secondary": [],
                    "corporate": [],
                },
            },
            {
                "id": "helmet.1666007",
                "title": "Tuntematon sotilas",
                "year": "2004",
                "formats": [{"value": "0/Book/", "translated": "Kirja"}],
                "buildings": [
                    {"value": "0/Helmet/", "translated": "Helmet-kirjastot"},
                    {"value": "2/Helmet/v/v30/", "translated": "Tikkurila"},
                ],
                "authors": {
                    "primary": {"Linna, Väinö": {"role": ["kirjoittaja"]}},
                    "secondary": [],
                    "corporate": [],
                },
            },
        ],
        "status": "OK",
    })
