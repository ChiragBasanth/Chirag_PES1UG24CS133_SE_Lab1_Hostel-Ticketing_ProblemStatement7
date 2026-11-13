# Lab 7 — Hospital Triage Priority

Chirag Basanth Bellavi · PES1UG24CS133

The first commit imports the assigned processor and adds Hypothesis tests for its three input formats. The original CLI raised a conversion error and the three no-crash properties failed. The second commit adds input validation and evidence from both runs.

Malformed vitals and ward codes return descriptive messages. Invalid BMI measurements return `None` and the CLI displays a message. The existing threshold checks and valid-input formats are preserved. Validation requires a positive heart rate, oxygen saturation from 0 to 100, finite numeric measurements, and positive bed numbers.

## Reproduce the final run

```sh
python -m pip install -r requirements.txt
python processor.py
python -m coverage run --branch --source=processor -m pytest -q test_processor.py
python -m coverage report -m --precision=2
```

31 tests passed. All 59 statements and 18 branches in `processor.py` were exercised. The evidence PDF and PNGs show the captured command output rendered as terminal images.

