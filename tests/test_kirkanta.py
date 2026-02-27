"""Tests for the Kirkanta API client."""

import httpx
import pytest
import respx

from helmet_agent.kirkanta import KirkantaClient

BASE_URL = "https://api.kirjastot.fi/v4"


@pytest.fixture
def client() -> KirkantaClient:
    return KirkantaClient()


class TestSearchLibraries:
    @respx.mock
    async def test_search_by_city(self, client: KirkantaClient):
        respx.get(f"{BASE_URL}/library").mock(
            return_value=httpx.Response(200, json={
                "type": "library",
                "total": 2,
                "items": [
                    {
                        "id": 84860,
                        "name": "Kallion kirjasto",
                        "shortName": "Kallio",
                        "type": "municipal",
                        "address": {
                            "street": "Viides linja 11",
                            "city": "Helsinki",
                            "zipcode": "00530",
                        },
                    },
                    {
                        "id": 84867,
                        "name": "Munkkiniemen kirjasto",
                        "shortName": "Munkkiniemi",
                        "type": "municipal",
                        "address": {
                            "street": "Riihitie 22",
                            "city": "Helsinki",
                            "zipcode": "00330",
                        },
                    },
                ],
            })
        )

        results = await client.search_libraries(city="helsinki")

        assert len(results) == 2
        assert results[0]["shortName"] == "Kallio"

    @respx.mock
    async def test_search_by_name(self, client: KirkantaClient):
        respx.get(f"{BASE_URL}/library").mock(
            return_value=httpx.Response(200, json={
                "type": "library",
                "total": 1,
                "items": [
                    {
                        "id": 84867,
                        "name": "Munkkiniemen kirjasto",
                        "shortName": "Munkkiniemi",
                        "type": "municipal",
                        "address": {
                            "street": "Riihitie 22",
                            "city": "Helsinki",
                            "zipcode": "00330",
                        },
                    },
                ],
            })
        )

        results = await client.search_libraries(city="helsinki", name="munkkiniemi")

        assert len(results) == 1
        assert results[0]["id"] == 84867

        request = respx.calls[0].request
        assert "munkkiniemi" in str(request.url)

    @respx.mock
    async def test_search_no_results(self, client: KirkantaClient):
        respx.get(f"{BASE_URL}/library").mock(
            return_value=httpx.Response(200, json={
                "type": "library",
                "total": 0,
                "items": [],
            })
        )

        results = await client.search_libraries(city="helsinki", name="nonexistent")
        assert results == []

    @respx.mock
    async def test_search_api_error_raises(self, client: KirkantaClient):
        respx.get(f"{BASE_URL}/library").mock(
            return_value=httpx.Response(500)
        )

        with pytest.raises(httpx.HTTPStatusError):
            await client.search_libraries(city="helsinki")


class TestGetSchedules:
    @respx.mock
    async def test_get_schedules(self, client: KirkantaClient):
        respx.get(f"{BASE_URL}/library/84867").mock(
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

        data = await client.get_schedules(84867)

        assert data["name"] == "Munkkiniemen kirjasto"
        assert len(data["schedules"]) == 2
        assert data["schedules"][0]["date"] == "2026-02-27"
        assert data["schedules"][0]["times"][0]["from"] == "09:00"

    @respx.mock
    async def test_get_schedules_with_date_range(self, client: KirkantaClient):
        respx.get(f"{BASE_URL}/library/84867").mock(
            return_value=httpx.Response(200, json={
                "type": "library",
                "total": 1,
                "data": {
                    "id": 84867,
                    "name": "Munkkiniemen kirjasto",
                    "schedules": [
                        {
                            "date": "2026-03-01",
                            "closed": True,
                            "times": [],
                        },
                    ],
                },
            })
        )

        data = await client.get_schedules(
            84867, period_start="2026-03-01", period_end="2026-03-01"
        )

        assert data["schedules"][0]["closed"] is True

        request = respx.calls[0].request
        url = str(request.url)
        assert "period.start=2026-03-01" in url
        assert "period.end=2026-03-01" in url

    @respx.mock
    async def test_get_schedules_closed_day(self, client: KirkantaClient):
        respx.get(f"{BASE_URL}/library/84860").mock(
            return_value=httpx.Response(200, json={
                "type": "library",
                "total": 1,
                "data": {
                    "id": 84860,
                    "name": "Kallion kirjasto",
                    "schedules": [
                        {
                            "date": "2026-03-01",
                            "closed": True,
                            "info": "Sunnuntai",
                            "times": [],
                        },
                    ],
                },
            })
        )

        data = await client.get_schedules(84860)

        assert data["schedules"][0]["closed"] is True
        assert data["schedules"][0]["info"] == "Sunnuntai"
