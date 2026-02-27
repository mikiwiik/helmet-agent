"""End-to-end smoke tests hitting real Finna and Kirkanta APIs.

Run with: uv run pytest -m integration
Skipped by default in normal test runs.
"""

import pytest

from helmet_agent import tools

pytestmark = pytest.mark.integration


class TestSearchMaterialsLive:
    async def test_search_author_at_branch(self):
        """UC-1: Search by author at a specific branch."""
        result = await tools.search_materials(
            query="väinö linna", author="väinö linna", branch="Munkkiniemi"
        )
        assert "Munkkiniemi" in result
        assert "result" in result.lower() or "Found" in result

    async def test_search_by_title(self):
        """UC-2: Search by title across all Helmet."""
        result = await tools.search_materials(
            query="tuntematon sotilas", title="tuntematon sotilas"
        )
        assert "Tuntematon sotilas" in result
        assert "helmet.finna.fi" in result

    async def test_search_with_city_filter(self):
        """UC-4: Search with city-level filter."""
        result = await tools.search_materials(
            query="dinosaurus", branch="Espoo", material_format="Book"
        )
        assert "result" in result.lower() or "Found" in result or "No results" in result

    async def test_ambiguous_branch(self):
        """UC-5: Ambiguous branch name returns options."""
        result = await tools.search_materials(query="books", branch="Haaga")
        assert "Etelä-Haaga" in result
        assert "Pohjois-Haaga" in result


class TestOpeningHoursLive:
    async def test_opening_hours(self):
        """UC-3: Get opening hours for a library."""
        result = await tools.get_opening_hours(library_name="Kallio")
        assert "Kallion kirjasto" in result or "Kallio" in result

    async def test_opening_hours_with_date(self):
        result = await tools.get_opening_hours(
            library_name="Oodi", date="2026-03-02"
        )
        assert "Oodi" in result
        assert "2026-03-02" in result


class TestListBranchesLive:
    async def test_list_helsinki(self):
        result = await tools.list_library_branches(city="Helsinki")
        assert "Munkkiniemi" in result
        assert "Pasila" in result
        assert "Oodi" in result
