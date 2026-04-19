"""
Applies all 12 compliance rules (Processing Manual + Compliance Annex) to a
list of raw sessions and returns a per-session ValidationResult.

Rule sources
------------
Rules  1–6  : Processing Manual  (basic field validation)
Rules  7–12 : Compliance Annex   (supplementary rules, access-restricted)
"""

import logging
from datetime import date

from app.core.config import (
    DEPT_BIN_AUTH,
    NORA_K_TERMINATION_DATE,
    Q4_2025_END,
    Q4_2025_START,
    VALID_BINS,
    VALID_CATEGORIES,
    VALID_DEPARTMENTS,
    VALID_PROCESSORS,
    VALUE_CEILING,
)
from app.core.models import Entry, RejectedEntry, Session, SessionResult

logger = logging.getLogger(__name__)


# ── Session-level checks ──────────────────────────────────────────────────────


def _session_violations(session: Session) -> list[str]:
    """
    Return rejection reasons that apply to the session as a whole.
    A non-empty list causes every entry in the session to be rejected.
    """
    ts_date = session.timestamp.date()
    violations: list[str] = []

    # Rule 1 — department must be an authorised facility division
    if session.department not in VALID_DEPARTMENTS:
        violations.append(f"invalid_department:{session.department}")

    # Rule 2 — processor must be a recognised employee code
    if session.processor not in VALID_PROCESSORS:
        violations.append(f"invalid_processor:{session.processor}")

    # Rule 6 — session must fall within the Q4 2025 processing window
    if not (Q4_2025_START <= ts_date <= Q4_2025_END):
        violations.append(f"outside_q4_window:{session.timestamp.isoformat()}")

    # Rule 12 — facility is closed on weekends (Mon=0 … Fri=4)
    if ts_date.weekday() >= 5:
        violations.append(f"weekend_session:{session.timestamp.isoformat()}")

    return violations


# ── Entry-level checks ────────────────────────────────────────────────────────


def _entry_violations(entry: Entry, session: Session) -> list[str]:
    """Return rejection reasons specific to a single entry."""
    violations: list[str] = []

    # Rule 3 — bin must be one of the four recognised signal bins
    if entry.bin not in VALID_BINS:
        violations.append(f"invalid_bin:{entry.bin}")

    # Rule 4 — category must be an authorised classification label
    if entry.category not in VALID_CATEGORIES:
        violations.append(f"invalid_category:{entry.category}")

    # Rule 5 — values must be strictly positive
    if entry.value <= 0:
        violations.append(f"non_positive_value:{entry.value}")

    # Rule 7 — Nora.K was terminated on Nov 15; her entries after that date are void
    if session.processor == "Nora.K" and session.timestamp.date() > NORA_K_TERMINATION_DATE:
        violations.append("terminated_processor:Nora.K")

    # Rules 8–9 — each department may only process its authorised bins
    authorised_bins = DEPT_BIN_AUTH.get(session.department, set())
    if entry.bin not in authorised_bins:
        violations.append(f"unauthorised_bin_for_dept:{entry.bin}@{session.department}")

    # Rule 10 — values must be strictly below the ceiling
    if entry.value >= VALUE_CEILING:
        violations.append(f"value_at_or_above_ceiling:{entry.value}")

    return violations


# ── Deduplication ─────────────────────────────────────────────────────────────


def _deduplicate(sessions: list[Session]) -> list[Session]:
    """
    Rule 11 — session_id values must be unique.
    When duplicates exist, retain the earliest session by timestamp.
    """
    seen: dict[str, Session] = {}
    for session in sorted(sessions, key=lambda s: s.timestamp):
        if session.session_id not in seen:
            seen[session.session_id] = session
        else:
            logger.debug("Discarding duplicate session_id '%s' (%s)", session.session_id, session.timestamp)

    removed = len(sessions) - len(seen)
    if removed:
        logger.info("Deduplication removed %d session(s) (Rule 11)", removed)

    return list(seen.values())


# ── Public interface ──────────────────────────────────────────────────────────


def validate(sessions: list[Session]) -> list[SessionResult]:
    """
    Validate all sessions and return one SessionResult per session.
    Sessions that fail session-level checks have all their entries rejected.
    """
    sessions = _deduplicate(sessions)
    results: list[SessionResult] = []

    for session in sessions:
        session_violations = _session_violations(session)

        if session_violations:
            # Propagate the session-level failure to every entry
            rejected = [RejectedEntry(ref=e.ref, reasons=session_violations) for e in session.entries]
            results.append(_build_result(session, valid_entries=[], rejected=rejected))
            continue

        valid_entries: list[Entry] = []
        rejected: list[RejectedEntry] = []

        for entry in session.entries:
            entry_violations = _entry_violations(entry, session)
            if entry_violations:
                rejected.append(RejectedEntry(ref=entry.ref, reasons=entry_violations))
            else:
                valid_entries.append(entry)

        results.append(_build_result(session, valid_entries, rejected))

    return results


def _build_result(session: Session, valid_entries: list[Entry], rejected: list[RejectedEntry]) -> SessionResult:
    return SessionResult(
        session_id=session.session_id,
        processor=session.processor,
        department=session.department,
        timestamp=session.timestamp,
        total_entries=len(session.entries),
        valid_entries=len(valid_entries),
        valid_sum=round(sum(e.value for e in valid_entries), 2),
        rejected=rejected,
    )
