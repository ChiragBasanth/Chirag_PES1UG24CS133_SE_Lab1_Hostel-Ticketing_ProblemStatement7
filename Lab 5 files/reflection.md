# Lab 5: Reflection

**Name:** Chirag Basanth Bellavi
**SRN:** PES1UG24CS133

**1. Which issues were the easiest and which were the hardest to fix?**
The easiest were the Flake8 blank-line errors (E302/E305): one regular expression fixed all of them and the report went from 10 findings to 0 without changing behaviour. Docstrings, the f-string and the rename of `assignDriver` were also quick. The hardest were the problems no tool reported. Fixing the bare `except: pass` was tricky because removing it showed what it had been hiding: the `"full"` trip in R3 caused a `TypeError` that was silently ignored, so I also had to add real input validation. The `global routes` statement also needed a small redesign (reload in place with `clear()` and `update()`).

**2. Did the tools report any false positives? How would you decide?**
Bandit B311 (`random.choice`) is a false positive in this program, because choosing a driver from a list has no security meaning. I decided by asking whether an attacker could gain anything from predicting the choice; here they cannot. I still switched to `secrets.choice` because it was a one-line change and avoided having to justify a `# nosec` comment. I did not use `# nosec` anywhere. The other findings I looked at were real: for example Pylint W0102 (mutable default) matched a bug I reproduced, where two calls returned the same list.

**3. How could static analysis be integrated into a real workflow?**
Run Flake8, Pylint and Bandit locally before each commit (for example with a pre-commit hook) and again in CI on every pull request. I checked that `pylint --fail-under=9.5` returns exit code 28 on the original file and 0 on the fixed one, and that `bandit -ll` returns 0 on the fixed file, so both can be used to fail a build. I have not set up CI in this lab; this is how I would do it. The tools only complement testing and review: on the original file none of them flagged the crash, the negative count or the `"full"` value.

**4. What tangible improvements did you see in code quality, security and runtime behaviour?**
Pylint went from 6.25 to 10.00, Bandit from 2 findings to 0, and Flake8 from 10 findings to 0. In behaviour, the original program ended with `KeyError: 'R3'` on every run (I ran it twice, exit code 1); the fixed one runs to the end. Bad data is now rejected instead of corrupting averages, errors are no longer silently swallowed, files are closed properly, and importing the module no longer runs the program. Documentation also improved because every function now has a docstring.
