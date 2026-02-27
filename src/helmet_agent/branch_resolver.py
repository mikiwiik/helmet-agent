"""Resolve natural-language branch names to Finna building codes."""

from difflib import SequenceMatcher
from typing import Any

from helmet_agent.finna import FinnaClient

# Minimum similarity score (0-1) for fuzzy matching
FUZZY_THRESHOLD = 0.5


class BranchResolver:
    """Maps branch names like 'Munkkiniemi' to Finna building codes."""

    def __init__(self) -> None:
        self._facets: list[dict[str, Any]] | None = None

    def load(self, facets: list[dict[str, Any]]) -> None:
        """Load building facets from a pre-fetched list."""
        self._facets = facets

    async def fetch(self, client: FinnaClient | None = None) -> None:
        """Fetch building facets from the Finna API and load them."""
        client = client or FinnaClient()
        facets = await client.get_building_facets()
        self.load(facets)

    def resolve(self, name: str) -> list[dict[str, Any]]:
        """Resolve a branch name to matching building facets.

        Returns a list of matches sorted by relevance (best first).
        Exact (case-insensitive) matches are returned alone.
        Fuzzy matches above the threshold are returned if no exact match.
        Returns empty list if nothing matches.

        Raises RuntimeError if facets have not been loaded yet.
        """
        if self._facets is None:
            raise RuntimeError("Branch data not loaded. Call load() or fetch() first.")

        query = name.lower()

        # Try exact match first
        for facet in self._facets:
            if facet["translated"].lower() == query:
                return [facet]

        # Fuzzy match
        scored: list[tuple[float, dict[str, Any]]] = []
        for facet in self._facets:
            translated = facet["translated"].lower()
            # Substring match gets a boost
            if query in translated or translated in query:
                score = 0.9
            else:
                score = SequenceMatcher(None, query, translated).ratio()
            if score >= FUZZY_THRESHOLD:
                scored.append((score, facet))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [facet for _, facet in scored]
