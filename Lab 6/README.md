# Lab 6 - Coverage analysis

Chirag Basanth Bellavi | PES1UG24CS133 | Section C

The hospital triage exercise is included in this Lab 6 directory. Source matches
SETAPESU26/L6_L7_07_hospital_traige_priority, Lab 6/hospital_triage_priority.py.

Install Python 3.12+, pytest and coverage, then run from this directory:

    python -m pip install -r requirements.txt
    python -m coverage run --data-file=.coverage.line --source=hospital_triage_priority -m pytest -q CodeCoverageTest_hospital_triage_priority.py
    python -m coverage report --data-file=.coverage.line -m
    python -m coverage run --data-file=.coverage.branch --branch --source=hospital_triage_priority -m pytest -q BranchCoverageTest_hospital_triage_priority.py
    python -m coverage report --data-file=.coverage.branch -m

Measured on 6 November 2026: line suite 15 passed, 45/45 statements (100%).
Branch suite 32 passed, 45/45 statements and 32/32 branches (100%); zero partial branches.
Each suite ran independently. Coverage is restricted to the application module.

Evidence: *_results.txt contains fresh command output; *_coverage.json contains
machine-readable results. *_coverage.png are browser screenshots of the actual
generated coverage.py HTML reports, not terminal-window screenshots.

Two separate commits contain the line and branch suites and their respective evidence.
The final PDF includes both coverage screenshots and explains the test design.
