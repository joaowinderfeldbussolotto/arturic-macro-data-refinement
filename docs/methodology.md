# Methodology & Anomalies — Q4 2025 Macro Data Refinement

## Approach

Process Q4 2025 session outputs from MDR, SA, and WB; sum values that pass a two-tier compliance framework.

### Step 1 — Discovering the Compliance Annex

The Compliance Annex required an access code (hint: *"consult your facility photograph for orientation."*).

EXIF from `docs/images/facility_exterior.png` returned **40.3652°N, 74.1639°W**, mapping to **Bell Works / former Bell Labs Holmdel**.

Using `notebooks/sign_radio_astronomy.png` and `notebooks/sign_exits.png` (radio astronomy marker + Bell Works exits sign), I built candidates from signage/context: `JANSKY`, `RADIO ASTRONOMY`, `BELL WORKS`, and road names.

I reproduced SHA-256 gate logic and tested candidates without brute force; only `JANSKY` matched.

### Step 2 — Data Ingestion

Input formats:
- **JSON / `.mdr`** — one session object per file with nested `entries`.
- **CSV** — one entry per row, grouped by `session_id`.
- **Plain text / `.txt`** — WB key/value session files with lines `REF`, `BIN`, `READING`, `TYPE`.

One ingester normalizes all formats into a shared `Session` Pydantic model before validation. Discovery is recursive across department folders; parsing is by format, not folder.

### Step 3 — Validation (12 Rules)

Rules 1–6 (Processing Manual): department, processor, bin, category, value sign, Q4 2025 timestamp scope.

Rules 7–12 (Compliance Annex): Nora.K boundary (entries strictly after November 15 are invalid), dept-bin authorization matrix, value < 1000.00, duplicate `session_id` deduplication (earliest timestamp retained), and weekday-only sessions.

Validation levels:
- Session-level checks (Rules 1, 2, 6, 12) invalidate all entries in a session.
- Entry-level checks (Rules 3–5, 7–10) apply per entry.

Entries can have multiple violation reasons; totals count violations.

## Anomalies Encountered

1. **Corrupted value fields** — 32 files had non-numeric values (`N/A`, `NULL`, `---`, `ERROR`) and were skipped at ingestion (22 `.mdr`, 6 `.csv`, 4 `.txt`).

2. **Invalid session identities** — 197 entry rejections were tied to non-authorized department codes (`HR`, `QA`, `TESTING`, `MR`) and 152 to unrecognized processor codes (`Cross.R`, `Harmon.D`, `Webb.T`). These session-level failures propagate to all entries.

3. **Cross-department duplicate session IDs** — 32 files were in wrong folders. 15 had a `session_id` collision with an existing session, always another department reusing an MDR-namespaced ID (for example, `MDR-0018` in MDR and SA). Rule 11 kept the earliest timestamp per `session_id`; all 15 retained the MDR original and discarded the cross-department copy. The remaining 17 cross-folder sessions were invalid-department traps (`HR`, `QA`, `TESTING`) or legitimate sessions rejected by the dept-bin authorization matrix.

4. **Department/bin authorization failures** — 186 violation counts were recorded for `unauthorised_bin_for_dept` (Rules 8–9): bins valid in isolation but forbidden for the session's department (for example, `SP` in MDR and `BL` in WB).

5. **Temporal and personnel compliance** — 143 entries were outside the Q4 2025 window, 110 occurred on weekends, and 107 were invalid due to Nora.K post-termination handling.

## Final Result

| Metric | Value |
|---|---|
| Sessions loaded | 383 |
| Sessions with valid data | 293 |
| Total entries loaded | 4,702 |
| Valid entries | 3,725 |
| **Final output metric** | **954,665.39** |
