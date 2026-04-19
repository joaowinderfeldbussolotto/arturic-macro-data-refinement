"""
Loads all session files from the sessions directory tree.

Three file formats are supported, reflecting the different systems used by
each department:

  .json / .mdr  — structured JSON with a nested entries array (MDR)
  .csv          — flat rows where each row is one entry (SA)
  .txt          — pipe-delimited key/value format used by WB

All formats are normalised into the shared Session model before any
validation takes place.
"""

import csv
import json
import logging
from datetime import datetime
from pathlib import Path

from app.core.models import Entry, Session

logger = logging.getLogger(__name__)


def _parse_json_session(path: Path) -> Session | None:
    """Parse a single .json or .mdr file into a Session. Returns None on error."""
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
        return Session(
            session_id=raw["session_id"],
            processor=raw["processor"],
            department=raw["department"],
            timestamp=datetime.fromisoformat(raw["timestamp"]),
            entries=[
                Entry(ref=e["ref"], bin=e["bin"], value=float(e["value"]), category=e["category"])
                for e in raw.get("entries", [])
            ],
        )
    except Exception as exc:
        logger.warning("Skipping %s — %s", path.name, exc)
        return None


def _parse_csv_sessions(path: Path) -> list[Session]:
    """
    Parse a CSV file into one or more Sessions.

    CSV rows share a session_id field; rows are grouped into a single Session
    per unique session_id. Each SA file contains exactly one session in practice,
    but the parser handles multiple sessions per file for robustness.
    """
    buckets: dict[str, dict] = {}
    try:
        with path.open(encoding="utf-8", newline="") as fh:
            for row in csv.DictReader(fh):
                sid = row["session_id"]
                if sid not in buckets:
                    buckets[sid] = {
                        "session_id": sid,
                        "processor": row["processor"],
                        "department": row["department"],
                        "timestamp": datetime.fromisoformat(row["timestamp"]),
                        "entries": [],
                    }
                buckets[sid]["entries"].append(
                    Entry(
                        ref=row["ref"],
                        bin=row["bin"],
                        value=float(row["output_metric"]),
                        category=row["classification"],
                    )
                )
    except Exception as exc:
        logger.warning("Skipping %s — %s", path.name, exc)
        return []

    return [Session(**b) for b in buckets.values()]


def _parse_txt_session(path: Path) -> Session | None:
    """
    Parse a WB-format .txt file into a Session. Returns None on error.

    Expected format:
        SESSION: <id>
        PROCESSOR: <name>
        DEPARTMENT: <dept>
        TIMESTAMP: <iso-like datetime>
        ---
        REF: <ref> | BIN: <bin> | READING: <value> | TYPE: <category>
        ...
    """
    try:
        lines = path.read_text(encoding="utf-8").splitlines()

        meta: dict[str, str] = {}
        entries: list[Entry] = []

        for line in lines:
            line = line.strip()
            if not line or line == "---":
                continue
            if line.startswith("REF:"):
                # REF: AX-E635 | BIN: AX | READING: 400.34 | TYPE: gamma
                parts = {k.strip(): v.strip() for k, v in (p.split(":", 1) for p in line.split("|"))}
                entries.append(
                    Entry(
                        ref=parts["REF"],
                        bin=parts["BIN"],
                        value=float(parts["READING"]),
                        category=parts["TYPE"],
                    )
                )
            elif ":" in line:
                key, _, value = line.partition(":")
                meta[key.strip()] = value.strip()

        return Session(
            session_id=meta["SESSION"],
            processor=meta["PROCESSOR"],
            department=meta["DEPARTMENT"],
            timestamp=datetime.fromisoformat(meta["TIMESTAMP"]),
            entries=entries,
        )
    except Exception as exc:
        logger.warning("Skipping %s — %s", path.name, exc)
        return None


def load_all_sessions(sessions_dir: str | Path) -> list[Session]:
    """
    Walk the sessions directory and load every supported file.
    Files that cannot be parsed are skipped with a warning.
    """
    base = Path(sessions_dir)
    sessions: list[Session] = []

    for path in sorted(base.rglob("*")):
        if path.suffix in {".json", ".mdr"}:
            session = _parse_json_session(path)
            if session:
                sessions.append(session)
        elif path.suffix == ".csv":
            sessions.extend(_parse_csv_sessions(path))
        elif path.suffix == ".txt":
            session = _parse_txt_session(path)
            if session:
                sessions.append(session)

    logger.info("Loaded %d session(s) from %s", len(sessions), base)
    return sessions
