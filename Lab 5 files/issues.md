# Lab 5: Static Code Analysis — Issues

**Name:** Chirag Basanth Bellavi
**SRN:** PES1UG24CS133
**Assigned repo:** L5_07_campus_shuttle (`shuttle_system.py`, Campus Shuttle Timetable & Fleet Tracker)

Line numbers refer to the ORIGINAL file. "Found by" says which tool reported it; "None" means it only showed up by running the program or reading the code.

| Issue | Type | Line(s) | Description | Fix Approach |
|-------|------|---------|-------------|--------------|
| Crash on looking up a removed route | Bug (High) — found by: None | 17, 55, 58 | `remove_route("R3")` deletes R3, then `average_load("R3")` raises `KeyError: 'R3'`. The original program crashed with this traceback on every run (exit code 1, checked twice). | Added `_get_route()` which raises a clear `ValueError` for unknown routes; `main()` catches it and prints a message instead of crashing. |
| Crash on unknown route typed by the user | Bug (High) — found by: None | 56–57 | Typing a route that does not exist (e.g. `R9`) gives `KeyError` from `routes[choice]`. | `main()` checks `choice in routes` and prints "No such route". Input is also stripped and upper-cased so `r1` works. |
| Negative passenger count accepted | Bug (High) — found by: None | 11–12, 49 | `add_trip_log("R2", -6)` stores -6. A route with only that trip has an average of -6.0, which makes the load report meaningless. | `add_trip_log` now validates the count and raises `ValueError` for negatives; nothing is stored. `main()` prints "Rejected trip". |
| Non-numeric passenger count accepted | Bug (High) — found by: None | 11–12, 50 | `add_trip_log("R3", "full")` stores a string. Later `sum()` fails with `TypeError`. | Same validation: only whole numbers (not `bool`, not `float`, not `str`) of 0 or more are accepted. |
| Bare `except: pass` hides errors | Security/Bug (Bandit Low, Pylint warning) — found by: Bandit B110, Pylint W0702, Flake8 E722 | 29–30 | Every error in `underused_routes` was swallowed. The `TypeError` from the `"full"` trip and the `ZeroDivisionError` from empty routes were hidden, so R3 was silently skipped. | Commit 1: catch only `(TypeError, ZeroDivisionError)` and log a warning (this made the hidden "full" error visible). Commit 2: removed the try/except entirely; `average_load` returns `None` for empty routes and bad data is rejected at input. |
| Mutable default argument | Bug (Medium) — found by: Pylint W0102 | 11 | `logs=[]` is created once, so every call that omits `logs` shares one list (checked: two calls returned the same list object with 2 entries). | Default is now `logs=None`; a new list is created inside the function. Checked that two calls now return separate lists. |
| `main()` runs on import | Design (Medium) — found by: None | 60 | `main()` is called at module level with no `__name__` guard, so importing the file runs the whole program (checked: importing the original crashed with the KeyError). | Wrapped in `if __name__ == "__main__":`. |
| Files opened without `with` / never closed | Resource leak (Medium) — found by: Pylint R1732 | 39–43 | The file is opened for writing and closed manually, then opened again for reading and never closed. | Both opens now use `with open(...)`. |
| `global` statement | Design (Medium) — found by: Pylint W0603 | 38 | `sync_fleet_data` rebinds the global `routes`. | Uses `json.load` into a local variable, then `routes.clear()` and `routes.update()`, so no `global` is needed. Behaviour is the same. |
| Average of an empty route divides by zero | Bug (Medium) — found by: None | 19–21 | `average_load` on a route with no trips raises `ZeroDivisionError` (checked on the original). It was only hidden by the bare except. | Returns `None` when there are no trips; `underused_routes` skips routes with no data. |
| No error handling when writing `fleet.json` | Bug (Medium) — found by: None | 37–43 | A read-only folder or full disk would crash the program with `OSError`. | `main()` catches `OSError` and prints "Could not sync fleet data". |
| `random.choice` flagged | Security (Bandit Low) — found by: Bandit B311 | 35 | Bandit warns that `random` is not for security use. Picking a driver is not security-sensitive, so this is a false positive in context. | Switched to `secrets.choice` so the finding is gone without a `# nosec`. No `# nosec` comments were used anywhere. |
| Unused argument `route_id` | Quality (Medium) — found by: Pylint W0613 | 33 | `assignDriver` ignored its argument, so it would "assign" a driver to a route that does not exist. | The function now checks the route exists (raises `ValueError` otherwise) before picking a driver. |
| Function name not snake_case | Style — found by: Pylint C0103 | 33 | `assignDriver` | Renamed to `assign_driver` and updated the call in `main()`. |
| Missing text encoding on `open()` | Quality — found by: Pylint W1514 | 39, 42 | Without `encoding`, the file encoding depends on the machine. | Added `encoding="utf-8"` to both opens. |
| Missing module docstring | Style — found by: Pylint C0114 | 1 | No description of the module. | Added a module docstring. |
| Missing function docstrings (7) | Style — found by: Pylint C0116 | 11, 16, 19, 23, 33, 37, 45 | No function had a docstring. | Added a short docstring to every function (including the new helper). |
| `%` string formatting | Style — found by: Pylint C0209 | 13 | Old-style `%` formatting. | Replaced with an f-string. |
| Missing blank lines between functions | Style — found by: Flake8 E302 (7 times) | 11, 16, 19, 23, 33, 37, 45 | Only one blank line before each function. | Two blank lines before every top-level function. |
| Missing blank lines after last function | Style — found by: Flake8 E305 | 60 | One blank line before the module-level call. | Two blank lines before `if __name__ == "__main__":`. |
| Line too long | Style — found by: Flake8 E501 | 13 | 82 characters (limit 79). | The new long `raise ValueError(...)` line was wrapped; the original line 13 was already rewritten as a shorter f-string. |

## Before / after summary

| Tool | Before | After Commit 1 (Bandit) | After Commit 2 (Pylint) | After Commit 3 (Flake8) |
|------|--------|-------------------------|-------------------------|-------------------------|
| Bandit | 2 findings (both Low: B110, B311) | 0 | 0 | 0 |
| Pylint | 6.25/10 (18 messages) | 6.53/10 | 10.00/10 | 10.00/10 |
| Flake8 | 10 findings | 9 (E722 gone) | 10 (new long line; blank-line style left as it was) | 0 |

Notes:
- I deliberately left the blank-line formatting alone in Commit 2 so that Commit 3 contains only the Flake8 fixes (one commit per tool).
- None of the four most serious problems (crashes, negative counts, `"full"`) were reported by any of the three tools; I found them by running the program.
- Reports are in `reports/before` and `reports/after`.

## Behaviour changes in the program

- Invalid trips (negative or non-numeric) are rejected with a message instead of being stored.
- The final lookups no longer crash: an unknown or removed route prints a message.
- Because "full" and -6 are rejected, R3 has no trips and R2's average is 4.0 (not -1.0). R2 is still flagged as under-used.
- The route prompt now accepts lower case and extra spaces.
