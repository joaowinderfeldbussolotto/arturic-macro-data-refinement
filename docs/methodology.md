# Methodology & Anomalies — Q4 2025 Macro Data Refinement

## Approach

The task required processing quarterly session output files from three departments (MDR, SA, WB) and computing the sum of all values that passed a two-tier compliance framework.

### Step 1 — Discovering the Compliance Annex

The Welcome Packet directed me to an employee portal whose Compliance Annex was locked behind an access code. The hint read: *"consult your facility photograph for orientation."*

I extracted EXIF metadata from `docs/images/facility_exterior.png` and recovered GPS coordinates at **40.3652°N, 74.1639°W**, which place the site at **Bell Works / former Bell Labs Holmdel**.

From that location, I used on-site visual evidence captured in `notebooks/sign_radio_astronomy.png` and `notebooks/sign_exits.png` (radio astronomy marker + Bell Works exits sign) to build access-code candidates directly from text on the signage (e.g., `JANSKY`, `RADIO ASTRONOMY`, `BELL WORKS`, road names), plus immediate historical context tied to those signs.

I then reproduced the portal's SHA-256 gate logic and verified each candidate without brute force. `JANSKY` was the only candidate that matched the gate hash and unlocked the Compliance Annex.

### Step 2 — Data Ingestion

Session files came in three formats:
- **JSON / `.mdr`** — one session object per file with a nested `entries` array.
- **CSV** — one entry per row, grouped by `session_id`.
- **Plain text / `.txt`** — WB-formatted key/value session files with entry lines (`REF`, `BIN`, `READING`, `TYPE`).

A unified ingester normalizes all three formats into a shared `Session` Pydantic model before any validation occurs.

### Step 3 — Validation (12 Rules)

Rules 1–6 (Processing Manual) cover department, processor, bin, category, value sign, and Q4 2025 timestamp scope. Rules 7–12 (Compliance Annex) add Nora.K's termination on November 15, the dept–bin authorization matrix, a value ceiling of < 1000.00, duplicate session ID deduplication (first-by-timestamp retained), and weekday-only sessions.

## Anomalies Encountered

1. **Corrupted value fields across all sources** — 32 files contained non-numeric values (`N/A`, `NULL`, `---`, `ERROR`) in value fields and were skipped at ingestion time (22 `.mdr`, 6 `.csv`, 4 `.txt`).

2. **Invalid session identities** — Session-level validation rejected large volumes tied to non-authorized department codes (`HR`, `QA`, `TESTING`) and unrecognized processor codes (`Cross.R`, `Harmon.D`, `Webb.T`). Rejection counts were 197 (`invalid_department`) and 152 (`invalid_processor`).

3. **Duplicate session IDs** — Rule 11 deduplication removed 15 sessions by retaining only the earliest timestamp per `session_id`.

4. **Department/bin authorization failures** — 186 entries were rejected by Rules 8–9 (`unauthorised_bin_for_dept`), primarily from bins that were valid in isolation but forbidden for the session's department.

5. **Temporal and personnel compliance** — 143 entries were outside the Q4 2025 window, 110 occurred on weekends, and 107 were invalid due to Nora.K post-termination handling.

## Final Result

| Metric | Value |
|---|---|
| Sessions loaded | 383 |
| Sessions with valid data | 293 |
| Total entries loaded | 4,702 |
| Valid entries | 3,725 |
| **Final output metric** | **954,665.39** |
