#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import glob
import os
from collections import Counter


def latest_csv(pattern: str) -> str:
    files = glob.glob(pattern)
    if not files:
        raise FileNotFoundError(f"no files for pattern: {pattern}")
    return max(files, key=os.path.getmtime)


def load_rows(path: str) -> list[dict]:
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def key(row: dict) -> tuple[str, str]:
    # stable key for comparing same SISBRA row across runs
    return (row.get("sisbra_time", ""), row.get("folder", ""))


def main() -> int:
    ap = argparse.ArgumentParser(description="Compare two run summary CSV files.")
    ap.add_argument("--w1-pattern", default="outputs/logs_w1/*_summary.csv")
    ap.add_argument("--wN-pattern", default="outputs/logs_w12/*_summary.csv")
    ap.add_argument("--max-diff-lines", type=int, default=20)
    args = ap.parse_args()

    f1 = latest_csv(args.w1_pattern)
    f2 = latest_csv(args.wN_pattern)

    r1 = load_rows(f1)
    r2 = load_rows(f2)

    c1 = Counter(x.get("match_status", "") for x in r1)
    c2 = Counter(x.get("match_status", "") for x in r2)

    print("w1_file:", f1)
    print("wN_file:", f2)
    print("w1_rows:", len(r1), "counts:", dict(c1))
    print("wN_rows:", len(r2), "counts:", dict(c2))

    m1 = {key(x): x for x in r1}
    m2 = {key(x): x for x in r2}

    only1 = sorted(set(m1) - set(m2))
    only2 = sorted(set(m2) - set(m1))

    status_diff = []
    for k in sorted(set(m1) & set(m2)):
        s1 = m1[k].get("match_status", "")
        s2 = m2[k].get("match_status", "")
        if s1 != s2:
            status_diff.append((k, s1, s2))

    print("only_in_w1:", len(only1))
    print("only_in_wN:", len(only2))
    print("status_diff:", len(status_diff))

    n = args.max_diff_lines
    if only1:
        print("\nonly_in_w1 sample:")
        for k in only1[:n]:
            print("-", k)
    if only2:
        print("\nonly_in_wN sample:")
        for k in only2[:n]:
            print("-", k)
    if status_diff:
        print("\nstatus_diff sample:")
        for k, s1, s2 in status_diff[:n]:
            print("-", k, "w1=", s1, "wN=", s2)

    if not only1 and not only2 and not status_diff:
        print("\nOK: runs are consistent for keys and status.")
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())

