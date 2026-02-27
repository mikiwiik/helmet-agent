"""Tests for the branch name resolver."""

import httpx
import pytest
import respx

from helmet_agent.branch_resolver import BranchResolver

SAMPLE_FACETS = [
    {"value": "0/Helmet/", "translated": "Helmet-kirjastot", "count": 795567},
    {"value": "1/Helmet/h/", "translated": "Helsinki", "count": 400000},
    {"value": "1/Helmet/e/", "translated": "Espoo", "count": 200000},
    {"value": "1/Helmet/v/", "translated": "Vantaa", "count": 150000},
    {"value": "1/Helmet/k/", "translated": "Kauniainen", "count": 30000},
    {"value": "2/Helmet/h/h01/", "translated": "Pasila", "count": 50000},
    {"value": "2/Helmet/h/h55/", "translated": "Munkkiniemi", "count": 20000},
    {"value": "2/Helmet/h/h82/", "translated": "Roihuvuori", "count": 15000},
    {"value": "2/Helmet/h/h90/", "translated": "Itäkeskus", "count": 25000},
    {"value": "2/Helmet/e/e13/", "translated": "Leppävaara", "count": 18000},
    {"value": "2/Helmet/e/e78/", "translated": "Etelä-Haaga", "count": 10000},
    {"value": "2/Helmet/v/v30/", "translated": "Tikkurila", "count": 22000},
]

FINNA_SEARCH_URL = "https://api.finna.fi/v1/search"


def _make_resolver(facets: list[dict] | None = None) -> BranchResolver:
    """Create a resolver pre-loaded with sample facets."""
    resolver = BranchResolver()
    resolver.load(facets or SAMPLE_FACETS)
    return resolver


class TestExactMatch:
    def test_exact_match_case_insensitive(self):
        resolver = _make_resolver()
        results = resolver.resolve("munkkiniemi")
        assert len(results) == 1
        assert results[0]["value"] == "2/Helmet/h/h55/"

    def test_exact_match_preserves_case(self):
        resolver = _make_resolver()
        results = resolver.resolve("Pasila")
        assert len(results) == 1
        assert results[0]["translated"] == "Pasila"

    def test_city_level_match(self):
        resolver = _make_resolver()
        results = resolver.resolve("Helsinki")
        assert len(results) == 1
        assert results[0]["value"] == "1/Helmet/h/"


class TestFuzzyMatch:
    def test_partial_match(self):
        resolver = _make_resolver()
        results = resolver.resolve("munkki")
        assert any(r["value"] == "2/Helmet/h/h55/" for r in results)

    def test_typo_tolerance(self):
        resolver = _make_resolver()
        results = resolver.resolve("munnkiniemi")
        assert any(r["value"] == "2/Helmet/h/h55/" for r in results)

    def test_no_match_returns_empty(self):
        resolver = _make_resolver()
        results = resolver.resolve("xyznonexistent")
        assert results == []


class TestAmbiguousMatch:
    def test_multiple_matches(self):
        """'haaga' should match Etelä-Haaga."""
        resolver = _make_resolver()
        results = resolver.resolve("haaga")
        assert len(results) >= 1
        values = [r["value"] for r in results]
        assert "2/Helmet/e/e78/" in values


class TestLoadFromApi:
    @respx.mock
    async def test_fetch_and_load(self):
        respx.get(FINNA_SEARCH_URL).mock(
            return_value=httpx.Response(200, json={
                "resultCount": 0,
                "facets": {"building": SAMPLE_FACETS},
                "status": "OK",
            })
        )

        resolver = BranchResolver()
        await resolver.fetch()

        results = resolver.resolve("Munkkiniemi")
        assert len(results) == 1
        assert results[0]["value"] == "2/Helmet/h/h55/"

    def test_resolve_before_load_raises(self):
        resolver = BranchResolver()
        with pytest.raises(RuntimeError, match="not loaded"):
            resolver.resolve("test")
