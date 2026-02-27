# Requirements

## Functional

### FR-1: Material search
The agent must search for library materials (books, audiobooks, DVDs, etc.) by author, title, or free-text query within the Helmet library network.

### FR-2: Branch filtering
The agent must filter results by library branch using natural-language names (e.g. "Munkkiniemi", "Oodi", "Kallio") resolved to Finna building codes.

### FR-3: Availability information
The agent must show which branches hold a given item. Note: real-time loan status (on shelf vs. checked out) is a known limitation of the Finna API.

### FR-4: Opening hours
The agent must answer questions about library opening hours using the Kirkanta API.

### FR-5: Natural language interface
Users interact with the agent via plain Finnish or English prompts. The agent decomposes questions into API calls and synthesizes a human-readable answer.

### FR-6: Record links
Responses must include direct links to the Helmet Finna record page (`https://helmet.finna.fi/Record/{id}`).

## Non-functional

### NFR-1: No authentication required
Both Finna and Kirkanta APIs are public. The agent must not require library credentials from users.

### NFR-2: Graceful degradation
If an API is unreachable or returns errors, the agent must inform the user clearly rather than crash.

### NFR-3: Response latency
Agent responses should complete within a reasonable time (~5-10s) for typical queries.

### NFR-4: Offline-safe branch resolution
Branch name-to-code mapping should be cached locally so it doesn't require a network call on every query.
