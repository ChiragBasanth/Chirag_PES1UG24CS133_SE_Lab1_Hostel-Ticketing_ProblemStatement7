import math

import pytest
from hypothesis import example, given, strategies as st

from processor import assign_ward_bed, compute_patient_bmi, parse_vitals_summary


@given(st.text() | st.none())
@example("70,nan,37")
def test_vitals_handles_arbitrary_input(value):
    assert isinstance(parse_vitals_summary(value), str)


@given(st.text() | st.none())
@example("70/0")
@example("70/1e-300")
@example("70/1e300")
def test_bmi_handles_arbitrary_input(value):
    result = compute_patient_bmi(value)
    assert result is None or (math.isfinite(result) and result >= 0)


@given(st.text() | st.none())
@example("XYZ-1")
def test_ward_handles_arbitrary_input(value):
    assert isinstance(assign_ward_bed(value), str)


@given(st.integers(1, 220), st.integers(0, 100), st.integers(30, 45))
def test_vitals_classification(hr, spo2, temp):
    status = "CRITICAL" if hr > 120 or spo2 < 90 or temp > 39 else "STABLE"
    assert parse_vitals_summary(f"{hr},{spo2},{temp}") == (
        f"Vitals: HR={float(hr)}, SpO2={float(spo2)}% - {status}"
    )


@given(st.integers(1, 400), st.integers(1, 250))
def test_bmi_calculation(weight, height_cm):
    height = height_cm / 100
    assert compute_patient_bmi(f"{weight}/{height}") == round(weight / height**2, 2)


@given(st.sampled_from([
    ("er", "Emergency Room"), ("icu", "Intensive Care Unit"),
    ("gen", "General Ward"), ("ped", "Pediatrics"),
]), st.integers(1, 1000))
def test_ward_assignment(ward, bed):
    code, name = ward
    assert assign_ward_bed(f" {code}-{bed:03d} ") == f"{name} Bed #{bed}"


@pytest.mark.parametrize("value", [None, "", "70,99", "70,99,37,extra",
                                    "x,99,37", "70,nan,37", "70,101,37"])
def test_invalid_vitals(value):
    assert parse_vitals_summary(value) == "Invalid vitals"


@pytest.mark.parametrize("value", [None, "70", "x/1.75", "70/0", "-1/2",
                                    "inf/2", "70/1e-300", "70/1e300", "1e308/0.01"])
def test_invalid_bmi(value):
    assert compute_patient_bmi(value) is None


@pytest.mark.parametrize("value", [None, "ICU", "ICU-x", "ICU-0", "XYZ-1"])
def test_invalid_ward(value):
    assert assign_ward_bed(value) == "Invalid allocation"


@pytest.mark.parametrize("inputs", ["70,98,37\n70/1.75\nICU-05\n",
                                    "bad\n70/0\nXYZ-1\n", ""])
def test_cli(inputs, monkeypatch, capsys):
    from io import StringIO
    from processor import main

    monkeypatch.setattr("sys.stdin", StringIO(inputs))
    main()
    output = capsys.readouterr().out
    if inputs.startswith("70"):
        assert "STABLE" in output and "BMI: 22.86" in output
        assert "Intensive Care Unit Bed #5" in output
    elif inputs:
        assert "Invalid vitals" in output and "BMI: Invalid measurements" in output
        assert "Invalid allocation" in output
    else:
        assert "Input ended." in output


def test_script_entry_point(monkeypatch, capsys):
    import runpy
    from io import StringIO

    monkeypatch.setattr("sys.stdin", StringIO("70,98,37\n70/1.75\nICU-05\n"))
    runpy.run_module("processor", run_name="__main__")
    assert "Intensive Care Unit Bed #5" in capsys.readouterr().out

