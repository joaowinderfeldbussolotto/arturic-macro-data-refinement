from datetime import date

# ── Rule 1-6: Basic validation (Processing Manual) ──────────────────────────

VALID_DEPARTMENTS = {"MDR", "SA", "WB"}

VALID_PROCESSORS = {
    "Arthur.B", "Clara.M", "Dr.Voss", "Felix.G",
    "James.L", "Lena.P", "Nora.K",
}

VALID_BINS = {"GR", "BL", "AX", "SP"}

VALID_CATEGORIES = {"alpha", "beta", "gamma", "delta"}

Q4_2025_START = date(2025, 10, 1)
Q4_2025_END   = date(2025, 12, 31)

# ── Rule 7-12: Supplementary Compliance Rules (Compliance Annex) ─────────────

# Rule 7: Nora.K terminated Nov 15, 2025
NORA_K_TERMINATION_DATE = date(2025, 11, 15)

# Rule 9: Department-Bin Authorization Matrix
DEPT_BIN_AUTH: dict[str, set[str]] = {
    "MDR": {"GR", "BL", "AX"},
    "SA":  {"SP", "BL"},
    "WB":  {"GR", "AX"},
}

# Rule 10: Value ceiling (exclusive)
VALUE_CEILING = 1000.0

# Note: Rule 8 (SP restricted to SA) is already covered by DEPT_BIN_AUTH
