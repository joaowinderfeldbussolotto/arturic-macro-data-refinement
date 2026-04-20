"""
tests/test_validator.py
Unit tests covering all 12 compliance rules.
"""

from datetime import datetime
import pytest

from app.core.models import Entry, Session
from app.services.validator import validate, _deduplicate as deduplicate_sessions


# ── Helpers ───────────────────────────────────────────────────────────────────

def make_session(
    session_id="MDR-TEST",
    processor="James.L",
    department="MDR",
    timestamp="2025-11-03T10:00:00",  # Monday, Q4 2025
    entries=None,
) -> Session:
    if entries is None:
        entries = [Entry(ref="GR-T001", bin="GR", value=100.0, category="alpha")]
    return Session(
        session_id=session_id,
        processor=processor,
        department=department,
        timestamp=datetime.fromisoformat(timestamp),
        entries=entries,
    )


def make_entry(ref="GR-X001", bin="GR", value=100.0, category="alpha") -> Entry:
    return Entry(ref=ref, bin=bin, value=value, category=category)


def run(sessions):
    return validate(sessions)


# ── Rule 1: Department validation ─────────────────────────────────────────────

def test_rule1_valid_department():
    for dept, allowed_bin in [("MDR", "GR"), ("SA", "BL"), ("WB", "GR")]:
        s = make_session(department=dept, entries=[make_entry(bin=allowed_bin)])
        results = run([s])
        assert results[0].valid_entries == 1, f"Dept {dept} should be valid"


def test_rule1_invalid_department():
    for dept in ["HR", "QA", "TESTING", "XX"]:
        s = make_session(department=dept)
        results = run([s])
        assert results[0].valid_entries == 0, f"Dept {dept} should be rejected"


# ── Rule 2: Processor validation ──────────────────────────────────────────────

def test_rule2_valid_processor():
    for proc in ["James.L", "Arthur.B", "Clara.M", "Felix.G", "Lena.P", "Dr.Voss"]:
        s = make_session(processor=proc)
        results = run([s])
        assert results[0].valid_entries == 1, f"Processor {proc} should be valid"


def test_rule2_invalid_processor():
    s = make_session(processor="Cross.R")
    results = run([s])
    assert results[0].valid_entries == 0


# ── Rule 3: Bin validation ────────────────────────────────────────────────────

def test_rule3_invalid_bin():
    for bad_bin in ["NV", "PH", "XX", "ZZ"]:
        s = make_session(entries=[make_entry(bin=bad_bin)])
        results = run([s])
        assert results[0].valid_entries == 0, f"Bin {bad_bin} should be rejected"


# ── Rule 4: Category validation ───────────────────────────────────────────────

def test_rule4_invalid_category():
    for bad_cat in ["epsilon", "omega", "sigma", "zeta"]:
        s = make_session(entries=[make_entry(category=bad_cat)])
        results = run([s])
        assert results[0].valid_entries == 0, f"Category {bad_cat} should be rejected"


# ── Rule 5: Positive value ────────────────────────────────────────────────────

def test_rule5_zero_value():
    s = make_session(entries=[make_entry(value=0.0)])
    assert run([s])[0].valid_entries == 0


def test_rule5_negative_value():
    s = make_session(entries=[make_entry(value=-50.0)])
    assert run([s])[0].valid_entries == 0


def test_rule5_positive_value():
    s = make_session(entries=[make_entry(value=0.01)])
    assert run([s])[0].valid_entries == 1


# ── Rule 6: Q4 2025 timestamp ─────────────────────────────────────────────────

def test_rule6_before_q4():
    s = make_session(timestamp="2025-09-30T23:59:59")
    assert run([s])[0].valid_entries == 0


def test_rule6_after_q4():
    s = make_session(timestamp="2026-01-01T00:00:00")
    assert run([s])[0].valid_entries == 0


def test_rule6_first_day_q4():
    s = make_session(timestamp="2025-10-01T08:00:00")  # Wednesday
    assert run([s])[0].valid_entries == 1


# ── Rule 7: Nora.K termination ────────────────────────────────────────────────

def test_rule7_nora_k_before_termination():
    # Nov 14 — still valid
    s = make_session(processor="Nora.K", timestamp="2025-11-14T10:00:00")
    assert run([s])[0].valid_entries == 1


def test_rule7_nora_k_on_termination_day_weekend_rejected():
    # Nov 15, 2025 is Saturday, so Rule 12 applies to the whole session.
    s = make_session(processor="Nora.K", timestamp="2025-11-15T10:00:00")
    result = run([s])[0]
    assert result.valid_entries == 0
    assert any(reason.startswith("weekend_session:") for reason in result.rejected[0].reasons)


def test_rule7_nora_k_after_termination_on_weekday():
    s = make_session(processor="Nora.K", timestamp="2025-11-20T10:00:00")
    result = run([s])[0]
    assert result.valid_entries == 0
    assert "terminated_processor:Nora.K" in result.rejected[0].reasons


# ── Rule 8+9: Dept-Bin authorization matrix ───────────────────────────────────

def test_rule9_mdr_authorized_bins():
    for b in ["GR", "BL", "AX"]:
        s = make_session(department="MDR", entries=[make_entry(bin=b)])
        assert run([s])[0].valid_entries == 1


def test_rule9_mdr_sp_unauthorized():
    s = make_session(department="MDR", entries=[make_entry(bin="SP")])
    assert run([s])[0].valid_entries == 0


def test_rule9_sa_authorized_bins():
    for b in ["SP", "BL"]:
        s = make_session(
            department="SA", processor="Clara.M",
            entries=[make_entry(bin=b)]
        )
        assert run([s])[0].valid_entries == 1


def test_rule9_wb_authorized_bins():
    for b in ["GR", "AX"]:
        s = make_session(
            department="WB", processor="Dr.Voss",
            entries=[make_entry(bin=b)]
        )
        assert run([s])[0].valid_entries == 1


def test_rule9_wb_bl_unauthorized():
    s = make_session(department="WB", processor="Dr.Voss", entries=[make_entry(bin="BL")])
    assert run([s])[0].valid_entries == 0


# ── Rule 10: Value ceiling ────────────────────────────────────────────────────

def test_rule10_value_at_ceiling():
    s = make_session(entries=[make_entry(value=1000.0)])
    assert run([s])[0].valid_entries == 0


def test_rule10_value_above_ceiling():
    s = make_session(entries=[make_entry(value=1000.01)])
    assert run([s])[0].valid_entries == 0


def test_rule10_value_below_ceiling():
    s = make_session(entries=[make_entry(value=999.99)])
    assert run([s])[0].valid_entries == 1


# ── Rule 11: Duplicate session IDs ───────────────────────────────────────────

def test_rule11_duplicate_session_ids():
    s1 = make_session(session_id="MDR-DUPE", timestamp="2025-10-06T08:00:00")
    s2 = make_session(session_id="MDR-DUPE", timestamp="2025-10-07T08:00:00")
    deduped = deduplicate_sessions([s1, s2])
    assert len(deduped) == 1
    assert deduped[0].timestamp == s1.timestamp  # first by timestamp kept


# ── Rule 12: Weekday only ─────────────────────────────────────────────────────

def test_rule12_saturday_rejected():
    s = make_session(timestamp="2025-10-04T10:00:00")  # Saturday
    assert run([s])[0].valid_entries == 0


def test_rule12_sunday_rejected():
    s = make_session(timestamp="2025-10-05T10:00:00")  # Sunday
    assert run([s])[0].valid_entries == 0


def test_rule12_monday_accepted():
    s = make_session(timestamp="2025-10-06T10:00:00")  # Monday
    assert run([s])[0].valid_entries == 1
