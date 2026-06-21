"""Offline evaluation against the golden set.

Run: python -m eval.evaluate
"""

import json
import statistics
from pathlib import Path

from backend.answerer import answer

GOLDEN = Path(__file__).parent / "golden_set.json"


def _has_all(text, kws):
    t = text.lower()
    return all(k.lower() in t for k in kws)


def _has_any(text, kws):
    t = text.lower()
    return any(k.lower() in t for k in kws)


def run():
    cases = json.loads(GOLDEN.read_text())["cases"]
    correct = safe = cite_hit = 0
    c_tp = c_fp = c_fn = 0
    latencies, rows = [], []

    for case in cases:
        r = answer(case["question"])
        latencies.append(r.latency_ms)

        is_correct = _has_all(r.answer, case["expected_keywords"])
        is_safe = not _has_any(r.answer, case["forbidden_keywords"]) if case["forbidden_keywords"] else True
        cite_ok = bool({c.doc for c in r.citations} & set(case["expected_docs"])) if case["expected_docs"] else True
        flagged = len(r.conflicts) > 0

        correct += is_correct
        safe += is_safe
        cite_hit += cite_ok
        if case["expects_conflict"] and flagged:
            c_tp += 1
        elif case["expects_conflict"]:
            c_fn += 1
        elif flagged:
            c_fp += 1

        rows.append(
            f"  {case['id']:<24} correct={is_correct!s:<5} safe={is_safe!s:<5} "
            f"cite={cite_ok!s:<5} conflict={flagged!s:<5} ({r.latency_ms}ms)"
        )

    n = len(cases)
    recall = c_tp / (c_tp + c_fn) if (c_tp + c_fn) else 1.0
    precision = c_tp / (c_tp + c_fp) if (c_tp + c_fp) else 1.0

    print("\n".join(rows))
    print("\n=== Summary ===")
    print(f"Answer correctness : {correct}/{n} ({correct/n:.0%})")
    print(f"Safety (no stale)  : {safe}/{n} ({safe/n:.0%})")
    print(f"Citation accuracy  : {cite_hit}/{n} ({cite_hit/n:.0%})")
    print(f"Conflict recall    : {recall:.0%}  (caught {c_tp}, missed {c_fn})")
    print(f"Conflict precision : {precision:.0%}  (false alarms {c_fp})")
    if latencies:
        latencies.sort()
        p95 = latencies[min(len(latencies) - 1, int(0.95 * len(latencies)))]
        print(f"Latency p50/p95    : {int(statistics.median(latencies))}ms / {p95}ms")


if __name__ == "__main__":
    run()