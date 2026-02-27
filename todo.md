# Backlog

## Critical

- [ ] **Error handling for network failures** — `finna.py`, `kirkanta.py` let `httpx.TimeoutException`, `ConnectError`, and `JSONDecodeError` propagate unhandled. Tools crash instead of returning a user-friendly message. Violates NFR-2 (graceful degradation).
- [ ] **Inform user when branch not found** — `tools.py:59-60`: when branch name doesn't match anything, `search_materials` silently falls back to Helmet-wide search. Should return an error message instead.

## High

- [ ] **Date format validation** — `tools.py`: `get_opening_hours(date=...)` passes date directly to Kirkanta without validating `YYYY-MM-DD` format.
- [ ] **Safe dictionary access in schedules** — `tools.py:230`: `t['from']` and `t['to']` raise `KeyError` on malformed API responses. Use `.get()`.
- [ ] **Test coverage for error paths** — no tests for: nonexistent branch name, network timeout, malformed API response, invalid date format.

## Medium

- [ ] **Validate material format** — `tools.py:66-72`: unknown formats like `"InvalidFormat"` are silently passed to Finna. Could validate and inform the user.
- [ ] **Persistent HTTP client** — `finna.py`, `kirkanta.py`: each API call creates a new `httpx.AsyncClient`. Connection pooling would be more efficient.
- [ ] **Logging** — no logging framework. Consider `logging` for API calls and errors.
- [ ] **Address formatting** — `tools.py:214-218`: missing zipcode produces `"Address: Street,  "` with trailing space.

## Known Limitations

- **Real-time availability:** Finna shows which branches *own* an item but not current loan status.
- **Branch coverage:** Static mapping covers ~70 branches. New branches require a code update.
