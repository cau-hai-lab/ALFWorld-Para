"""Score an ALFWorld-Para run.

Takes a results file holding one {"id": ..., "success": ...} per record and
prints the table the paper reports: success rate by object-axis type, then the
per-cell breakdown.

    python data/score.py results.jsonl
    python data/score.py results.jsonl --by cell
    python data/score.py results.jsonl --by task_type

The results file is JSON Lines or a JSON array. Only `id` and `success` are
read; any other field is ignored, so a run log can be passed as is. `success`
may be a bool, 0/1, or a float reward, in which case anything above 0 counts.
Records from originals.json score as the None split; pass both files' results
together to report it.
"""

import argparse
import json
import os
import sys
from collections import defaultdict

HERE = os.path.dirname(os.path.realpath(__file__))

# Paper column name per object-axis type. The object axis is what drives the
# failure, so the headline table splits on it and pools the action axis.
COLUMN = {
    "none": "None",
    "lexical_addition_deletion": "Addition",
    "lexical_same_polarity": "Same-Polarity",
}
ORDER = ["None", "Addition", "Same-Polarity"]


def load_records():
    out = {}
    for name in ("alfworld_para.json", "originals.json"):
        path = os.path.join(HERE, name)
        if os.path.exists(path):
            for r in json.load(open(path)):
                out[r["id"]] = r
    return out


def load_results(path):
    text = open(path, encoding="utf-8").read().strip()
    rows = json.loads(text) if text.startswith("[") else [
        json.loads(line) for line in text.splitlines() if line.strip()
    ]
    out = {}
    for row in rows:
        if "id" not in row or "success" not in row:
            continue
        v = row["success"]
        out[row["id"]] = bool(v) if isinstance(v, bool) else float(v) > 0
    return out


def table(title, groups, total_n):
    width = max(len(k) for k in groups) + 2
    print(f"\n{title}")
    print(f"  {'':{width}} {'n':>6} {'SR (%)':>8}")
    for key, hits in groups.items():
        n = len(hits)
        sr = 100.0 * sum(hits) / n if n else float("nan")
        print(f"  {key:{width}} {n:>6} {sr:>8.1f}")
    allhits = [h for hits in groups.values() for h in hits]
    sr = 100.0 * sum(allhits) / len(allhits) if allhits else float("nan")
    print(f"  {'ALL':{width}} {len(allhits):>6} {sr:>8.1f}")
    if len(allhits) < total_n:
        print(f"  ({total_n - len(allhits)} of {total_n} records missing from the results file)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("results", help="JSONL or JSON array of {id, success}")
    ap.add_argument("--by", default="object_type",
                    choices=["object_type", "cell", "task_type", "axis", "template_id"])
    args = ap.parse_args()

    records = load_records()
    if not records:
        sys.exit("alfworld_para.json not found next to this script")
    results = load_results(args.results)
    if not results:
        sys.exit("no {id, success} rows found in the results file")

    unknown = [i for i in results if i not in records]
    if unknown:
        print(f"warning: {len(unknown)} result ids are not in the dataset, e.g. {unknown[:3]}")

    groups = defaultdict(list)
    for rid, ok in results.items():
        r = records.get(rid)
        if r is None:
            continue
        key = r[args.by]
        if args.by == "object_type":
            key = COLUMN.get(key, key)
        groups[key].append(ok)

    if args.by == "object_type":
        groups = {k: groups[k] for k in ORDER if k in groups}
    else:
        groups = dict(sorted(groups.items()))

    scored = {i for i in results if i in records}
    table(f"ALFWorld-Para success rate by {args.by}",
          groups, len([r for r in records if r in scored] or scored) or len(records))


if __name__ == "__main__":
    main()
