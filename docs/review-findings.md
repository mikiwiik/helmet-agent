# Project Review Findings

Review date: 2026-02-27. All 56 tests passing (49 unit + 7 integration).

---

## Critical — fix before production use

### 1. No error handling for network failures
**Files:** `finna.py`, `kirkanta.py`

Both API clients let `httpx.TimeoutException`, `httpx.ConnectError`, and `json.JSONDecodeError` propagate unhandled. The MCP tool crashes instead of returning a user-friendly message.

This violates **NFR-2** (graceful degradation).

### 2. Silent fallback when branch not found
**File:** `tools.py:59-60`

When the user provides a branch name that doesn't match anything (e.g. "Xyz"), the resolver returns an empty list and `search_materials` silently falls back to a Helmet-wide search. The user sees results but thinks they're from "Xyz".

Should return an error message instead.

---

## High — should fix

### 3. No date format validation
**File:** `tools.py:173`

`get_opening_hours(date=...)` passes the date string directly to Kirkanta without validating `YYYY-MM-DD` format. Invalid formats like "03-02-2026" are passed through silently.

### 4. Unsafe dictionary access in schedule formatting
**File:** `tools.py:230`

`t['from']` and `t['to']` use direct key access. If the Kirkanta API returns a malformed schedule entry, this raises `KeyError`. Should use `.get()`.

### 5. Missing test coverage for error paths
No tests for:
- Nonexistent branch name (empty resolver result)
- Network timeout / connection error
- Malformed API responses
- Invalid date format

---

## Medium — nice to have

### 6. Unknown material format accepted silently
**File:** `tools.py:66-72`

`material_format="InvalidFormat"` gets turned into `format:"0/InvalidFormat/"` and passed to Finna, which returns no results without explanation. Could validate against the known format map and inform the user.

### 7. HTTP client created per request
**Files:** `finna.py:43`, `kirkanta.py:37`

Each API call creates and tears down a new `httpx.AsyncClient`. A persistent client with connection pooling would be more efficient. Acceptable for a low-traffic MCP server but worth noting.

### 8. No logging
No logging framework configured. Difficult to debug issues in production. Consider adding `logging` for API calls and errors.

### 9. README test count outdated
**File:** `README.md:46`

Says "49 tests" — actual count is 56 (49 unit + 7 integration).

### 10. Address formatting edge case
**File:** `tools.py:214-218`

If `street` is present but `zipcode` is empty, output has a trailing comma and extra space: `"Address: Streetname,  "`.

---

## Positive findings

- Clean separation of concerns (clients, resolver, tools, server)
- 56 tests with good mix of unit and integration
- Type hints on all public functions
- Fuzzy branch matching handles ambiguity well
- All documentation present and mostly up to date
- No security concerns (public APIs, httpx handles URL encoding)
- Passes ruff linting
