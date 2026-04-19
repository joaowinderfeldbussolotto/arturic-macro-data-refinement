"""
scripts/run_pipeline.py

Standalone runner — loads all sessions, applies all 12 validation rules,
and prints a summary report with the final output metric.

Usage:
    python -m scripts.run_pipeline
    python -m scripts.run_pipeline --sessions path/to/sessions
"""

import argparse
import sys
from pathlib import Path
from collections import defaultdict

# Allow running from project root
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app.services.ingester import load_all_sessions
from app.services.validator import validate


def main():
    parser = argparse.ArgumentParser(description="Arturic Industries — MDR Pipeline")
    parser.add_argument(
        "--sessions",
        default="data",
        help="Path to the sessions directory (default: ./data)",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Print per-session breakdown",
    )
    args = parser.parse_args()

    sessions_dir = Path(args.sessions)
    if not sessions_dir.exists():
        print(f"[ERROR] Sessions directory not found: {sessions_dir}", file=sys.stderr)
        sys.exit(1)

    # ── Load ──────────────────────────────────────────────────────────────────
    print(f"\nLoading sessions from: {sessions_dir.resolve()}")
    raw_sessions = load_all_sessions(sessions_dir)
    print(f"  Raw sessions loaded : {len(raw_sessions)}")

    # ── Validate ──────────────────────────────────────────────────────────────
    results = validate(raw_sessions)

    # ── Aggregate ─────────────────────────────────────────────────────────────
    total_entries   = sum(r.total_entries for r in results)
    valid_entries   = sum(r.valid_entries for r in results)
    rejected_entries = total_entries - valid_entries
    final_sum       = round(sum(r.valid_sum for r in results), 2)

    # Rejection reason breakdown
    reason_counts: dict[str, int] = defaultdict(int)
    for r in results:
        for rej in r.rejected:
            for reason in rej.reasons:
                # Normalize to rule label
                label = reason.split(":")[0]
                reason_counts[label] += 1

    # ── Print summary ─────────────────────────────────────────────────────────
    print("\n" + "=" * 55)
    print("  ARTURIC INDUSTRIES — Q4 2025 REFINEMENT REPORT")
    print("=" * 55)
    print(f"  Sessions loaded          : {len(raw_sessions)}")
    print(f"  Sessions with valid data : {sum(1 for r in results if r.valid_entries > 0)}")
    print(f"  Total entries loaded     : {total_entries}")
    print(f"  Valid entries            : {valid_entries}")
    print(f"  Rejected entries         : {rejected_entries}")
    print(f"\n  ──────────────────────────────────────────────")
    print(f"  FINAL OUTPUT METRIC      : {final_sum:>12.2f}")
    print(f"  ──────────────────────────────────────────────")

    if reason_counts:
        print("\n  Rejection breakdown:")
        for reason, count in sorted(reason_counts.items(), key=lambda x: -x[1]):
            print(f"    {reason:<45} {count:>5}")

    # ── Per-department breakdown ──────────────────────────────────────────────
    dept_sums: dict[str, float] = defaultdict(float)
    dept_counts: dict[str, int] = defaultdict(int)
    for r in results:
        dept_sums[r.department] += r.valid_sum
        dept_counts[r.department] += r.valid_entries

    print("\n  Per-department breakdown:")
    for dept in sorted(dept_sums):
        print(f"    {dept}: {dept_counts[dept]} entries → {dept_sums[dept]:.2f}")

    # ── Verbose: per-session detail ───────────────────────────────────────────
    if args.verbose:
        print("\n  Per-session detail:")
        print(f"  {'Session':<15} {'Dept':<6} {'Processor':<12} {'Valid':>5} {'Sum':>10}")
        print("  " + "-" * 55)
        for r in sorted(results, key=lambda x: x.session_id):
            print(
                f"  {r.session_id:<15} {r.department:<6} {r.processor:<12} "
                f"{r.valid_entries:>5} {r.valid_sum:>10.2f}"
            )

    print()
    return final_sum


if __name__ == "__main__":
    main()
