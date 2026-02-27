"""Tests for the branch name resolver."""

from helmet_agent.branch_resolver import BRANCH_MAP, CITY_MAP, BranchResolver


def _make_resolver() -> BranchResolver:
    """Create a resolver loaded with static data."""
    resolver = BranchResolver()
    resolver.load_static()
    return resolver


class TestExactMatch:
    def test_exact_match_case_insensitive(self):
        resolver = _make_resolver()
        results = resolver.resolve("munkkiniemi")
        assert len(results) == 1
        assert results[0]["value"] == "2/Helmet/h/h33/"

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

    def test_vallila_is_h55(self):
        """Verify Vallila maps to h55 (not Munkkiniemi)."""
        resolver = _make_resolver()
        results = resolver.resolve("Vallila")
        assert len(results) == 1
        assert results[0]["value"] == "2/Helmet/h/h55/"


class TestFuzzyMatch:
    def test_partial_match(self):
        resolver = _make_resolver()
        results = resolver.resolve("munkki")
        assert any(r["value"] == "2/Helmet/h/h33/" for r in results)

    def test_typo_tolerance(self):
        resolver = _make_resolver()
        results = resolver.resolve("munnkiniemi")
        assert any(r["value"] == "2/Helmet/h/h33/" for r in results)

    def test_no_match_returns_empty(self):
        resolver = _make_resolver()
        results = resolver.resolve("xyznonexistent")
        assert results == []


class TestAmbiguousMatch:
    def test_haaga_matches_both(self):
        """'haaga' should match both Etelä-Haaga and Pohjois-Haaga."""
        resolver = _make_resolver()
        results = resolver.resolve("haaga")
        values = [r["value"] for r in results]
        assert "2/Helmet/h/h32/" in values  # Etelä-Haaga
        assert "2/Helmet/h/h40/" in values  # Pohjois-Haaga


class TestListBranches:
    def test_list_helsinki_branches(self):
        resolver = _make_resolver()
        branches = resolver.list_branches(city="Helsinki")
        values = [b["value"] for b in branches]
        assert "2/Helmet/h/h33/" in values  # Munkkiniemi
        assert "2/Helmet/h/h01/" in values  # Pasila
        # No Espoo branches
        assert not any(v.startswith("2/Helmet/e/") for v in values)

    def test_list_espoo_branches(self):
        resolver = _make_resolver()
        branches = resolver.list_branches(city="Espoo")
        values = [b["value"] for b in branches]
        assert "2/Helmet/e/e01/" in values  # Sello
        assert not any(v.startswith("2/Helmet/h/") for v in values)

    def test_list_unknown_city_returns_empty(self):
        resolver = _make_resolver()
        branches = resolver.list_branches(city="Turku")
        assert branches == []

    def test_list_all_branches(self):
        resolver = _make_resolver()
        branches = resolver.list_branches()
        assert len(branches) == len(BRANCH_MAP)


class TestAutoLoad:
    def test_resolve_auto_loads(self):
        """Resolver auto-loads static data on first resolve call."""
        resolver = BranchResolver()
        results = resolver.resolve("Oodi")
        assert len(results) == 1
        assert results[0]["value"] == "2/Helmet/h/h00/"

    def test_list_branches_auto_loads(self):
        """list_branches auto-loads static data on first call."""
        resolver = BranchResolver()
        branches = resolver.list_branches(city="Helsinki")
        assert len(branches) > 0


class TestStaticData:
    def test_branch_map_has_entries(self):
        assert len(BRANCH_MAP) > 60

    def test_city_map_has_four_cities(self):
        assert len(CITY_MAP) == 4
        assert "helsinki" in CITY_MAP
        assert "espoo" in CITY_MAP
        assert "vantaa" in CITY_MAP
        assert "kauniainen" in CITY_MAP
