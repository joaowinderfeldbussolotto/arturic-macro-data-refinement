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

A unified ingester normalizes all three formats into a shared `Session` Pydantic model before any validation occurs. Files are discovered via recursive walk across all department folders, regardless of location — cross-department files are parsed by format, not by folder.

### Step 3 — Validation (12 Rules)

Rules 1–6 (Processing Manual) cover department, processor, bin, category, value sign, and Q4 2025 timestamp scope. Rules 7–12 (Compliance Annex) add Nora.K's termination on November 15, the dept–bin authorization matrix, a value ceiling of < 1000.00, duplicate session ID deduplication (first-by-timestamp retained), and weekday-only sessions.

Validation operates at two levels: session-level checks (Rules 1, 2, 6, 12) that invalidate all entries in a session if triggered, and entry-level checks (Rules 3–5, 7–10) applied individually. A single entry may accumulate multiple violation reasons; the rejection breakdown counts all violations, not just the first per entry.

## Anomalies Encountered

1. **Corrupted value fields** — 32 files contained non-numeric values (`N/A`, `NULL`, `---`, `ERROR`) in value fields and were skipped at ingestion time (22 `.mdr`, 6 `.csv`, 4 `.txt`).

2. **Invalid session identities** — 197 entry-rejections were tied to non-authorized department codes (`HR`, `QA`, `TESTING`, `MR`) and 152 to unrecognized processor codes (`Cross.R`, `Harmon.D`, `Webb.T`). These are session-level failures that propagate to every entry in the session.

3. **Cross-department duplicate session IDs** — The dataset contains 32 files placed in the "wrong" department folder. Of these, 15 carry a `session_id` that collides with an existing session in the correct folder — always a different department using an MDR-namespaced ID (e.g., `MDR-0018` exists both as an MDR session and as an SA session). Rule 11 deduplication retains the earliest timestamp per `session_id`, which in all 15 cases was the MDR original, discarding the cross-department copy. The remaining 17 unique cross-folder sessions are either invalid-department traps (`HR`, `QA`, `TESTING`) or legitimate sessions whose entries are rejected by the dept–bin authorization matrix.

4. **Department/bin authorization failures** — 186 violation counts were recorded for `unauthorised_bin_for_dept` (Rules 8–9). These are entries using bins valid in isolation but forbidden for their session's department (e.g., `SP` in MDR, `BL` in WB).

5. **Temporal and personnel compliance** — 143 entries were outside the Q4 2025 window, 110 occurred on weekends, and 107 were invalid due to Nora.K post-termination handling.

## Final Result

| Metric | Value |
|---|---|
| Sessions loaded | 383 |
| Sessions with valid data | 293 |
| Total entries loaded | 4,702 |
| Valid entries | 3,725 |
| **Final output metric** | **954,665.39** |
