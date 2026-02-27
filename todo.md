# Backlog

## Critical

- [ ] **Handle network failures gracefully** — `finna.py`, `kirkanta.py`: timeouts, connection errors, and malformed JSON propagate as unhandled exceptions. Wrap API calls in try/except and return user-friendly messages. (Violates NFR-2.)
- [ ] **Report unknown branch names** — `tools.py`: when the branch resolver returns no matches (e.g. "Xyz"), `search_materials` silently falls back to a Helmet-wide search. Should tell the user the branch wasn't found.

## High

- [ ] **Validate date format** — `tools.py`: `get_opening_hours(date=...)` passes the string directly to Kirkanta. Invalid formats like "03-02-2026" fail silently. Validate `YYYY-MM-DD` before calling the API.
- [ ] **Use safe dictionary access in schedules** — `tools.py`: `t['from']` / `t['to']` will crash on malformed Kirkanta responses. Use `.get()` with fallbacks.
- [ ] **Add error-path tests** — no coverage for: unknown branch name, network timeout, malformed API response, invalid date format.

## Medium

- [ ] **Validate material format** — `tools.py`: unknown formats like `"InvalidFormat"` are silently turned into `format:"0/InvalidFormat/"`. Validate against the known map and inform the user.
- [ ] **Reuse HTTP connections** — `finna.py`, `kirkanta.py`: each call creates a new `httpx.AsyncClient`. A persistent client with connection pooling would reduce latency.
- [ ] **Add logging** — no logging framework. Add `logging` for API calls, errors, and resolver hits to aid debugging.
- [ ] **Fix address formatting** — `tools.py`: when zipcode is missing, the address line has a trailing comma and extra space.
