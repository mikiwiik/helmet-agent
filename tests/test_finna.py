"""Tests for the Finna API client."""

import httpx
import pytest
import respx

from helmet_agent.finna import FinnaClient

BASE_URL = "https://api.finna.fi/v1"


@pytest.fixture
def client() -> FinnaClient:
    return FinnaClient()


class TestSearch:
    @respx.mock
    async def test_search_by_author(self, client: FinnaClient):
        respx.get(f"{BASE_URL}/search").mock(
            return_value=httpx.Response(200, json={
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
                            {"value": "2/Helmet/v/v40/", "translated": "Koivukylä"},
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
        )

        result = await client.search("väinö linna", search_type="Author")

        assert result["resultCount"] == 2
        assert len(result["records"]) == 2
        assert result["records"][0]["title"] == "Tuntematon sotilas"

        request = respx.calls[0].request
        assert "lookfor" in str(request.url)
        assert "Author" in str(request.url)

    @respx.mock
    async def test_search_with_building_filter(self, client: FinnaClient):
        respx.get(f"{BASE_URL}/search").mock(
            return_value=httpx.Response(200, json={
                "resultCount": 1,
                "records": [{"id": "helmet.123", "title": "Test"}],
                "status": "OK",
            })
        )

        result = await client.search(
            "test",
            filters=['building:"2/Helmet/h/h55/"'],
        )

        assert result["resultCount"] == 1
        request = respx.calls[0].request
        assert "building" in str(request.url)

    @respx.mock
    async def test_search_with_format_filter(self, client: FinnaClient):
        respx.get(f"{BASE_URL}/search").mock(
            return_value=httpx.Response(200, json={
                "resultCount": 0,
                "records": [],
                "status": "OK",
            })
        )

        result = await client.search(
            "sinuhe",
            filters=['format:"0/Book/"'],
        )

        assert result["resultCount"] == 0
        assert result["records"] == []

    @respx.mock
    async def test_search_custom_limit_and_page(self, client: FinnaClient):
        respx.get(f"{BASE_URL}/search").mock(
            return_value=httpx.Response(200, json={
                "resultCount": 50,
                "records": [{"id": f"helmet.{i}", "title": f"Book {i}"} for i in range(5)],
                "status": "OK",
            })
        )

        result = await client.search("test", limit=5, page=2)

        assert len(result["records"]) == 5
        request = respx.calls[0].request
        url = str(request.url)
        assert "limit=5" in url
        assert "page=2" in url

    @respx.mock
    async def test_search_default_fields(self, client: FinnaClient):
        respx.get(f"{BASE_URL}/search").mock(
            return_value=httpx.Response(200, json={
                "resultCount": 0, "records": [], "status": "OK",
            })
        )

        await client.search("test")

        request = respx.calls[0].request
        url = str(request.url)
        for field in ["id", "title", "authors", "formats", "buildings", "year"]:
            assert f"field%5B%5D={field}" in url or f"field[]={field}" in url

    @respx.mock
    async def test_search_api_error_raises(self, client: FinnaClient):
        respx.get(f"{BASE_URL}/search").mock(
            return_value=httpx.Response(500, json={
                "status": "ERROR",
                "statusMessage": "Internal server error",
            })
        )

        with pytest.raises(httpx.HTTPStatusError):
            await client.search("test")


class TestGetRecord:
    @respx.mock
    async def test_get_record(self, client: FinnaClient):
        respx.get(f"{BASE_URL}/record").mock(
            return_value=httpx.Response(200, json={
                "resultCount": 1,
                "records": [
                    {
                        "id": "helmet.2280900",
                        "title": "Tuntematon sotilas",
                        "year": "2017",
                        "buildings": [
                            {"value": "2/Helmet/h/h01/", "translated": "Pasila"},
                            {"value": "2/Helmet/h/h82/", "translated": "Roihuvuori"},
                        ],
                    }
                ],
                "status": "OK",
            })
        )

        record = await client.get_record("helmet.2280900")

        assert record["id"] == "helmet.2280900"
        assert record["title"] == "Tuntematon sotilas"
        assert len(record["buildings"]) == 2

        request = respx.calls[0].request
        assert "helmet.2280900" in str(request.url)

    @respx.mock
    async def test_get_record_not_found(self, client: FinnaClient):
        respx.get(f"{BASE_URL}/record").mock(
            return_value=httpx.Response(200, json={
                "resultCount": 0,
                "records": [],
                "status": "OK",
            })
        )

        with pytest.raises(ValueError, match="not found"):
            await client.get_record("helmet.nonexistent")


class TestGetBuildingFacets:
    @respx.mock
    async def test_get_building_facets(self, client: FinnaClient):
        respx.get(f"{BASE_URL}/search").mock(
            return_value=httpx.Response(200, json={
                "resultCount": 100000,
                "facets": {
                    "building": [
                        {"value": "0/Helmet/", "translated": "Helmet-kirjastot", "count": 795567},
                        {"value": "1/Helmet/h/", "translated": "Helsinki", "count": 400000},
                        {"value": "2/Helmet/h/h01/", "translated": "Pasila", "count": 50000},
                        {"value": "2/Helmet/h/h55/", "translated": "Munkkiniemi", "count": 20000},
                    ],
                },
                "status": "OK",
            })
        )

        facets = await client.get_building_facets()

        assert len(facets) == 4
        assert facets[0]["value"] == "0/Helmet/"
        assert facets[3]["translated"] == "Munkkiniemi"

        request = respx.calls[0].request
        url = str(request.url)
        assert "facet" in url
        assert "building" in url

    @respx.mock
    async def test_get_building_facets_with_parent(self, client: FinnaClient):
        respx.get(f"{BASE_URL}/search").mock(
            return_value=httpx.Response(200, json={
                "resultCount": 100000,
                "facets": {
                    "building": [
                        {"value": "2/Helmet/h/h01/", "translated": "Pasila", "count": 50000},
                        {"value": "2/Helmet/h/h55/", "translated": "Munkkiniemi", "count": 20000},
                    ],
                },
                "status": "OK",
            })
        )

        facets = await client.get_building_facets(parent="1/Helmet/h/")

        assert len(facets) == 2
        request = respx.calls[0].request
        assert "building" in str(request.url)
