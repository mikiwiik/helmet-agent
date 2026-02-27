"""Resolve natural-language branch names to Finna building codes."""

from difflib import SequenceMatcher
from typing import Any

# Minimum similarity score (0-1) for fuzzy matching
FUZZY_THRESHOLD = 0.5

# Static mapping of branch names to Finna building codes.
# Collected from actual Finna search results across all Helmet libraries.
# Excludes children's departments (codes ending in 'l/').
BRANCH_MAP: dict[str, str] = {
    # Espoo
    "Sello": "2/Helmet/e/e01/",
    "Tapiola": "2/Helmet/e/e10/",
    "Laajalahti": "2/Helmet/e/e14/",
    "Otaniemi": "2/Helmet/e/e15/",
    "Haukilahti": "2/Helmet/e/e17/",
    "Iso Omena": "2/Helmet/e/e23/",
    "Suurpelto": "2/Helmet/e/e25/",
    "Nöykkiö": "2/Helmet/e/e30/",
    "Lippulaiva": "2/Helmet/e/e32/",
    "Saunalahti": "2/Helmet/e/e33/",
    "Viherlaakso": "2/Helmet/e/e71/",
    "Laaksolahti": "2/Helmet/e/e73/",
    "Entresse": "2/Helmet/e/e76/",
    "Kauklahti": "2/Helmet/e/e78/",
    "Karhusuo": "2/Helmet/e/e81/",
    "Kalajärvi": "2/Helmet/e/e97/",
    # Helsinki
    "Oodi": "2/Helmet/h/h00/",
    "Pasila": "2/Helmet/h/h01/",
    "Rikhardinkatu": "2/Helmet/h/h13/",
    "Jätkäsaari": "2/Helmet/h/h18/",
    "Suomenlinna": "2/Helmet/h/h19/",
    "Lauttasaari": "2/Helmet/h/h20/",
    "Töölö": "2/Helmet/h/h25/",
    "Pikku Huopalahti": "2/Helmet/h/h30/",
    "Etelä-Haaga": "2/Helmet/h/h32/",
    "Munkkiniemi": "2/Helmet/h/h33/",
    "Pitäjänmäki": "2/Helmet/h/h37/",
    "Pohjois-Haaga": "2/Helmet/h/h40/",
    "Malminkartano": "2/Helmet/h/h41/",
    "Kannelmäki": "2/Helmet/h/h42/",
    "Kallio": "2/Helmet/h/h53/",
    "Vallila": "2/Helmet/h/h55/",
    "Arabianranta": "2/Helmet/h/h56/",
    "Kalasatama": "2/Helmet/h/h58/",
    "Käpylä": "2/Helmet/h/h61/",
    "Maunula": "2/Helmet/h/h63/",
    "Oulunkylä": "2/Helmet/h/h64/",
    "Paloheinä": "2/Helmet/h/h67/",
    "Malmi": "2/Helmet/h/h70/",
    "Viikki": "2/Helmet/h/h71/",
    "Pukinmäki": "2/Helmet/h/h72/",
    "Tapanila": "2/Helmet/h/h73/",
    "Suutarila": "2/Helmet/h/h74/",
    "Tapulikaupunki": "2/Helmet/h/h75/",
    "Puistola": "2/Helmet/h/h76/",
    "Jakomäki": "2/Helmet/h/h77/",
    "Herttoniemi": "2/Helmet/h/h80/",
    "Roihuvuori": "2/Helmet/h/h82/",
    "Laajasalo": "2/Helmet/h/h84/",
    "Itäkeskus": "2/Helmet/h/h90/",
    "Myllypuro": "2/Helmet/h/h92/",
    "Kontula": "2/Helmet/h/h94/",
    "Vuosaari": "2/Helmet/h/h98/",
    "Pasila kirjavarasto": "2/Helmet/h/hva/",
    # Kauniainen
    "Kauniainen": "2/Helmet/k/k01/",
    # Vantaa
    "Hakunila": "2/Helmet/v/v20/",
    "Länsimäki": "2/Helmet/v/v28/",
    "Tikkurila": "2/Helmet/v/v30/",
    "Koivukylä": "2/Helmet/v/v40/",
    "Lumo": "2/Helmet/v/v45/",
    "Point": "2/Helmet/v/v51/",
    "Myyrmäki": "2/Helmet/v/v60/",
    "Martinlaakso": "2/Helmet/v/v62/",
    "Pähkinärinne": "2/Helmet/v/v68/",
    "Mosaiikki": "2/Helmet/v/v70/",
}

# City-level codes
CITY_MAP: dict[str, str] = {
    "helsinki": "1/Helmet/h/",
    "espoo": "1/Helmet/e/",
    "vantaa": "1/Helmet/v/",
    "kauniainen": "1/Helmet/k/",
}


class BranchResolver:
    """Maps branch names like 'Munkkiniemi' to Finna building codes."""

    def __init__(self) -> None:
        self._entries: list[dict[str, Any]] = []
        self._loaded = False

    def load_static(self) -> None:
        """Load the static branch mapping."""
        self._entries = [
            {"translated": name, "value": code}
            for name, code in BRANCH_MAP.items()
        ]
        # Add city-level entries
        for city, code in CITY_MAP.items():
            self._entries.append({"translated": city.capitalize(), "value": code})
        self._loaded = True

    def resolve(self, name: str) -> list[dict[str, Any]]:
        """Resolve a branch name to matching building entries.

        Returns a list of matches sorted by relevance (best first).
        Exact (case-insensitive) matches are returned alone.
        Fuzzy matches above the threshold are returned if no exact match.
        Returns empty list if nothing matches.
        """
        if not self._loaded:
            self.load_static()

        query = name.lower()

        # Try exact match first
        for entry in self._entries:
            if entry["translated"].lower() == query:
                return [entry]

        # Fuzzy match
        scored: list[tuple[float, dict[str, Any]]] = []
        for entry in self._entries:
            translated = entry["translated"].lower()
            # Substring match gets a boost
            if query in translated or translated in query:
                score = 0.9
            else:
                score = SequenceMatcher(None, query, translated).ratio()
            if score >= FUZZY_THRESHOLD:
                scored.append((score, entry))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [entry for _, entry in scored]

    def list_branches(self, city: str | None = None) -> list[dict[str, Any]]:
        """List all branches, optionally filtered by city."""
        if not self._loaded:
            self.load_static()

        if city:
            city_prefix = CITY_MAP.get(city.lower())
            if not city_prefix:
                return []
            branch_prefix = city_prefix.replace("1/", "2/")
            return [
                e for e in self._entries
                if e["value"].startswith(branch_prefix)
            ]
        return [e for e in self._entries if e["value"].startswith("2/Helmet/")]
