import pytest
from hospital_triage_priority import process_triage_wards, monitor_oxygen_manifolds


def make_ward(patients, accepting=True, tier="general", icu=False):
    return {
        "is_accepting": accepting,
        "tier": tier,
        "icu_standby": icu,
        "patients": patients,
    }


# ---------- process_triage_wards: validation branches ----------

def test_single_normal_patient():
    wards = [make_ward([{"spo2": 98, "hr": 72, "unconscious": False}])]
    result = process_triage_wards(wards, 10)
    assert result["acuity_score"] == 10
    assert result["status"] == "TRIAGE_STABLE"


def test_invalid_wards_not_a_list():
    with pytest.raises(ValueError):
        process_triage_wards("not a list", 10)


def test_invalid_negative_default_score():
    with pytest.raises(ValueError):
        process_triage_wards([], -1)


def test_zero_default_score_is_valid():
    result = process_triage_wards([make_ward([{"spo2": 98, "hr": 72}])], 0)
    assert result == {"acuity_score": 0, "status": "NO_URGENT_CASES"}


# ---------- loop / ward-level branches ----------

def test_empty_ward_list_loop_never_runs():
    assert process_triage_wards([], 10) == {"acuity_score": 0, "status": "NO_URGENT_CASES"}


def test_ward_not_accepting_is_skipped():
    wards = [make_ward([{"spo2": 98, "hr": 72}], accepting=False, icu=True)]
    assert process_triage_wards(wards, 10)["acuity_score"] == 0


def test_ward_with_no_patients_loop_exits_immediately():
    result = process_triage_wards([make_ward([])], 10)
    assert result["status"] == "NO_URGENT_CASES"


def test_ward_missing_optional_keys_uses_defaults():
    result = process_triage_wards([{"is_accepting": True, "patients": [{}]}], 7)
    assert result["acuity_score"] == 7


def test_icu_standby_true_adds_25():
    wards = [make_ward([{"spo2": 98, "hr": 72}], icu=True)]
    assert process_triage_wards(wards, 10)["acuity_score"] == 35


def test_icu_standby_false_adds_nothing():
    wards = [make_ward([{"spo2": 98, "hr": 72}], icu=False)]
    assert process_triage_wards(wards, 10)["acuity_score"] == 10


# ---------- patient-level branches ----------

def test_invalid_spo2_flagged():
    result = process_triage_wards([make_ward([{"spo2": 0, "hr": 80}])], 10)
    assert result["acuity_score"] == 0


def test_invalid_heart_rate_flagged():
    result = process_triage_wards([make_ward([{"spo2": 95, "hr": 0}])], 10)
    assert result["acuity_score"] == 0


def test_negative_vitals_flagged():
    result = process_triage_wards([make_ward([{"spo2": -1, "hr": -1}])], 10)
    assert result["acuity_score"] == 0


def test_unconscious_general_ward_adds_100():
    wards = [make_ward([{"spo2": 95, "hr": 80, "unconscious": True}])]
    assert process_triage_wards(wards, 10)["acuity_score"] == 100


def test_unconscious_outpatient_resets_and_breaks():
    wards = [make_ward(
        [
            {"spo2": 95, "hr": 80},
            {"spo2": 95, "hr": 80, "unconscious": True},
            {"spo2": 95, "hr": 80},
        ],
        tier="outpatient",
    )]
    result = process_triage_wards(wards, 10)
    assert result == {"acuity_score": 0, "status": "NO_URGENT_CASES"}


def test_conscious_outpatient_is_normal():
    wards = [make_ward([{"spo2": 95, "hr": 80}], tier="outpatient")]
    assert process_triage_wards(wards, 10)["acuity_score"] == 10


def test_low_spo2_adds_60():
    wards = [make_ward([{"spo2": 85, "hr": 80}])]
    assert process_triage_wards(wards, 10)["acuity_score"] == 60


def test_spo2_boundary_90_is_normal():
    wards = [make_ward([{"spo2": 90, "hr": 80}])]
    assert process_triage_wards(wards, 10)["acuity_score"] == 10


def test_high_heart_rate_adds_60():
    wards = [make_ward([{"spo2": 98, "hr": 130}])]
    assert process_triage_wards(wards, 10)["acuity_score"] == 60


def test_heart_rate_boundary_120_is_normal():
    wards = [make_ward([{"spo2": 98, "hr": 120}])]
    assert process_triage_wards(wards, 10)["acuity_score"] == 10


# ---------- final status branches ----------

def test_ward_alert_with_five_flagged_entries():
    patients = [{"spo2": 0, "hr": 80} for _ in range(5)]
    result = process_triage_wards([make_ward(patients)], 10)
    assert result == {"acuity_score": 0, "status": "WARD_ALERT"}


def test_four_flagged_entries_is_not_alert():
    patients = [{"spo2": 0, "hr": 80} for _ in range(4)]
    result = process_triage_wards([make_ward(patients)], 10)
    assert result["status"] == "NO_URGENT_CASES"


def test_no_urgent_cases_when_score_zero():
    wards = [make_ward([{"spo2": 98, "hr": 72}], accepting=False)]
    assert process_triage_wards(wards, 10)["status"] == "NO_URGENT_CASES"


def test_triage_stable_when_score_positive():
    wards = [make_ward([{"spo2": 85, "hr": 80}])]
    assert process_triage_wards(wards, 10)["status"] == "TRIAGE_STABLE"


# ---------- monitor_oxygen_manifolds ----------

def test_oxygen_empty_streams_no_data():
    assert monitor_oxygen_manifolds([]) == "NO_DATA"


def test_oxygen_none_streams_no_data():
    assert monitor_oxygen_manifolds(None) == "NO_DATA"


def test_oxygen_two_consecutive_drops_failure():
    assert monitor_oxygen_manifolds([[5.0, 3.5, 3.0]]) == "PRESSURE_FAILURE"


def test_oxygen_failure_found_in_later_manifold():
    assert monitor_oxygen_manifolds([[5.0, 5.0], [3.0, 3.0]]) == "PRESSURE_FAILURE"


def test_oxygen_single_drop_is_normal():
    assert monitor_oxygen_manifolds([[5.0, 3.5, 5.0]]) == "PRESSURE_NORMAL"


def test_oxygen_streak_resets_between_drops():
    assert monitor_oxygen_manifolds([[3.0, 5.0, 3.0, 5.0]]) == "PRESSURE_NORMAL"


def test_oxygen_boundary_4_is_normal():
    assert monitor_oxygen_manifolds([[4.0, 4.0]]) == "PRESSURE_NORMAL"


def test_oxygen_empty_manifold_is_normal():
    assert monitor_oxygen_manifolds([[]]) == "PRESSURE_NORMAL"
