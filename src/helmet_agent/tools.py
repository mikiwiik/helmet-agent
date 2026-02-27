"""MCP tool definitions for the Helmet library agent."""

from helmet_agent.branch_resolver import BranchResolver
from helmet_agent.finna import FinnaClient
from helmet_agent.kirkanta import KirkantaClient
from helmet_agent.server import mcp

# Shared instances — initialized lazily
_finna = FinnaClient()
_kirkanta = KirkantaClient()
_branch_resolver: BranchResolver | None = None


async def _ensure_resolver() -> BranchResolver:
    """Ensure the branch resolver is initialized."""
    global _branch_resolver
    if _branch_resolver is None:
        resolver = BranchResolver()
        await resolver.fetch(_finna)
        _branch_resolver = resolver
    return _branch_resolver


@mcp.tool()
async def search_materials(
    query: str,
    author: str | None = None,
    title: str | None = None,
    branch: str | None = None,
    material_format: str | None = None,
) -> str:
    """Search for books, audiobooks, DVDs and other materials in Helsinki Helmet libraries.

    Examples:
    - search_materials(query="väinö linna", author="väinö linna", branch="Munkkiniemi")
    - search_materials(query="tuntematon sotilas", title="tuntematon sotilas")
    - search_materials(query="dinosaurus", branch="Espoo", material_format="Book")

    Args:
        query: Search keywords (required).
        author: Filter by author name. When set, searches the Author field.
        title: Filter by title. When set, searches the Title field.
        branch: Library branch or city name (e.g. "Munkkiniemi", "Kallio", "Espoo").
        material_format: Material type — "Book", "Sound" (audiobooks/music), "Video", or omit for all.
    """
    # Determine search type
    search_type = "AllFields"
    if author:
        search_type = "Author"
        query = author
    elif title:
        search_type = "Title"
        query = title

    # Build filters — always restrict to Helmet
    filters: list[str] = ['building:"0/Helmet/"']

    # Resolve branch name to building code
    if branch:
        resolver = await _ensure_resolver()
        matches = resolver.resolve(branch)
        if len(matches) > 1 and branch.lower() != matches[0]["translated"].lower():
            # Ambiguous — report options instead of guessing
            options = ", ".join(m["translated"] for m in matches[:5])
            return f"Multiple branches match '{branch}': {options}. Did you mean one of these? Please specify."
        if matches:
            best = matches[0]
            filters.append(f'building:"{best["value"]}"')

    # Format filter
    if material_format:
        format_map = {
            "book": "0/Book/",
            "sound": "0/Sound/",
            "video": "0/Video/",
        }
        fmt = format_map.get(material_format.lower(), f"0/{material_format}/")
        filters.append(f'format:"{fmt}"')

    result = await _finna.search(query, search_type=search_type, filters=filters, limit=20)

    records = result.get("records", [])
    total = result.get("resultCount", 0)

    if not records:
        return f"No results found for '{query}' in Helmet libraries."

    lines = [f"Found {total} result(s). Showing first {len(records)}:\n"]
    for rec in records:
        rec_id = rec.get("id", "")
        rec_title = rec.get("title", "Unknown title")
        year = rec.get("year", "")
        formats = ", ".join(f.get("translated", "") for f in rec.get("formats", []))
        authors = ", ".join(rec.get("authors", {}).get("primary", {}).keys())
        branches = [
            b["translated"] for b in rec.get("buildings", [])
            if b["value"].startswith("2/Helmet/")
        ]

        line = f"- **{rec_title}**"
        if authors:
            line += f" — {authors}"
        if year:
            line += f" ({year})"
        if formats:
            line += f" [{formats}]"
        if branches:
            line += f"\n  Branches: {', '.join(branches)}"
        line += f"\n  Link: https://helmet.finna.fi/Record/{rec_id}"
        lines.append(line)

    return "\n".join(lines)


@mcp.tool()
async def get_record_detail(record_id: str) -> str:
    """Get full details for a specific library record by its Finna ID.

    Example: get_record_detail(record_id="helmet.2280900")

    Args:
        record_id: The Finna record ID (e.g. "helmet.2280900").
    """
    try:
        rec = await _finna.get_record(record_id)
    except ValueError:
        return f"Record '{record_id}' not found."

    rec_title = rec.get("title", "Unknown title")
    year = rec.get("year", "")
    formats = ", ".join(f.get("translated", "") for f in rec.get("formats", []))
    authors = ", ".join(rec.get("authors", {}).get("primary", {}).keys())
    branches = [
        b["translated"] for b in rec.get("buildings", [])
        if b["value"].startswith("2/Helmet/")
    ]

    lines = [f"**{rec_title}**"]
    if authors:
        lines.append(f"Author: {authors}")
    if year:
        lines.append(f"Year: {year}")
    if formats:
        lines.append(f"Format: {formats}")
    if branches:
        lines.append(f"Available at: {', '.join(branches)}")
    lines.append(f"Link: https://helmet.finna.fi/Record/{record_id}")

    return "\n".join(lines)


@mcp.tool()
async def list_library_branches(city: str = "Helsinki") -> str:
    """List all Helmet library branches in a city.

    Examples:
    - list_library_branches(city="Helsinki")
    - list_library_branches(city="Espoo")

    Args:
        city: City name — "Helsinki", "Espoo", "Vantaa", or "Kauniainen".
    """
    resolver = await _ensure_resolver()

    city_map = {
        "helsinki": "1/Helmet/h/",
        "espoo": "1/Helmet/e/",
        "vantaa": "1/Helmet/v/",
        "kauniainen": "1/Helmet/k/",
    }

    city_prefix = city_map.get(city.lower())
    if not city_prefix:
        return f"Unknown city '{city}'. Supported: Helsinki, Espoo, Vantaa, Kauniainen."

    branch_prefix = city_prefix.replace("1/", "2/")

    branches = [
        f for f in (resolver._facets or [])
        if f["value"].startswith(branch_prefix)
    ]

    if not branches:
        return f"No branches found for {city}."

    lines = [f"Helmet library branches in {city} ({len(branches)}):\n"]
    for b in sorted(branches, key=lambda x: x["translated"]):
        lines.append(f"- {b['translated']}")

    return "\n".join(lines)


@mcp.tool()
async def get_opening_hours(library_name: str, date: str | None = None) -> str:
    """Get opening hours for a Helmet library.

    Examples:
    - get_opening_hours(library_name="Kallio")
    - get_opening_hours(library_name="Oodi", date="2026-03-02")
    - get_opening_hours(library_name="Munkkiniemi")

    Args:
        library_name: Library name or short name (e.g. "Kallio", "Munkkiniemi", "Oodi").
        date: Optional date (YYYY-MM-DD) to get hours for a specific day. Omit for the current week.
    """
    # Search Kirkanta for the library
    libraries = await _kirkanta.search_libraries(name=library_name)

    # If no exact match, try broader search and filter locally
    if not libraries:
        all_libs = await _kirkanta.search_libraries()
        libraries = [
            lib for lib in all_libs
            if library_name.lower() in lib.get("name", "").lower()
            or library_name.lower() in lib.get("shortName", "").lower()
        ]

    if not libraries:
        return f"No library found matching '{library_name}'."

    lib = libraries[0]
    lib_id = lib["id"]

    # Fetch schedules
    data = await _kirkanta.get_schedules(
        lib_id,
        period_start=date,
        period_end=date,
    )
    schedules = data.get("schedules", [])
    address = data.get("address", lib.get("address", {}))

    lines = [f"**{data.get('name', lib.get('name', library_name))}**"]
    if address:
        street = address.get("street", "")
        zipcode = address.get("zipcode", "")
        city = address.get("city", "")
        if street:
            lines.append(f"Address: {street}, {zipcode} {city}")

    if schedules:
        lines.append("\nOpening hours:")
        for s in schedules:
            date = s.get("date", "")
            if s.get("closed"):
                info = s.get("info", "")
                lines.append(f"  {date}: Closed{f' ({info})' if info else ''}")
            else:
                times = s.get("times", [])
                for t in times:
                    lines.append(f"  {date}: {t['from']} – {t['to']}")
    else:
        lines.append("No schedule information available.")

    return "\n".join(lines)
