#!/usr/bin/env python3
"""Read only FAFB exports; emit a small, traceable circuit for local use."""
import argparse
import collections
import csv
import gzip
import hashlib
import json
from pathlib import Path

TYPES = {"LC4", "LPLC2", "DNp01", "DNp02", "DNp11"}
FILES = ["fafb-consolidated_cell_types.csv.gz", "fafb-classification.csv.gz",
         "fafb-neurons.csv.gz", "fafb-connections_princeton.csv.gz"]


def rows(path):
    with gzip.open(path, "rt", newline="") as stream:
        yield from csv.DictReader(stream)


def extract(root):
    neurons = {}
    duplicates = 0
    for row in rows(root / FILES[0]):
        if row["primary_type"] not in TYPES:
            continue
        ident = row["root_id"]
        if ident in neurons:
            if neurons[ident]["type"] != row["primary_type"]:
                raise ValueError(f"Conflicting primary types: {ident}")
            duplicates += 1
        neurons[ident] = {"id": ident, "type": row["primary_type"]}
    for row in rows(root / FILES[1]):
        if row["root_id"] in neurons:
            neurons[row["root_id"]]["side"] = row["side"]
    for row in rows(root / FILES[2]):
        if row["root_id"] in neurons:
            neurons[row["root_id"]].update(nt=row["nt_type"],
                                           nt_confidence=float(row["nt_type_score"]))
    pairs = collections.defaultdict(collections.Counter)
    reference = collections.Counter()
    scanned = 0
    for row in rows(root / FILES[3]):
        scanned += 1
        pre, post = row["pre_root_id"], row["post_root_id"]
        if pre in neurons and post in neurons:
            count = int(row["syn_count"])
            if count <= 0:
                raise ValueError("Non-positive synapse count")
            pairs[pre, post][row["neuropil"]] += count
            reference[neurons[pre]["type"], neurons[post]["type"]] += count
    cells = sorted(neurons.values(), key=lambda n: int(n["id"]))
    # Unknown identities must be investigated rather than silently made excitatory.
    unsupported = sorted({n.get("nt") for n in cells} - {"ACH", "GABA", "GLUT", ""}, key=str)
    if unsupported:
        raise ValueError(f"Unsupported NT identities: {unsupported}")
    sources = []
    for name in FILES:
        with (root / name).open("rb") as stream:
            digest = hashlib.file_digest(stream, "sha256").hexdigest()
        sources.append({"path": name, "sha256": digest})
    return {"schema": 1, "name": "fafb-escape-candidate",
            "provenance": {"sources": sources, "license": "unverified: local use only",
                           "release": "unverified; filenames suggest FAFB v783",
                           "selection": "induced subgraph on exact primary types",
                           "types": sorted(TYPES), "duplicate_annotations": duplicates,
                           "connection_rows_scanned": scanned,
                           "unknown_nt_ids": [n["id"] for n in cells if not n["nt"]],
                           "unknown_nt_policy": "preserve anatomical edges; disable their outgoing efficacy",
                           "limitations": ["truncated circuit", "synthetic receptive fields",
                                           "predicted neurotransmitters", "unvalidated dynamics"]},
            "dynamics": {"dt_ms": 1.0, "membrane_tau_ms": 20.0,
                         "synapse_tau_ms": 5.0, "gain": 0.004,
                         "threshold": 1.0, "refractory_ms": 2,
                         "rate_tau_ms": 30.0, "delay_ms": 1.0,
                         "origin": "engineered normalized LIF; not measured physiology"},
            "neurons": cells,
            "edges": [{"pre": a, "post": b, "count": sum(counts.values()),
                       "neuropils": dict(sorted(counts.items()))}
                      for (a, b), counts in sorted(pairs.items())],
            "type_synapses": {f"{a}->{b}": n for (a, b), n in sorted(reference.items())}}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=Path, default=Path.cwd())
    parser.add_argument("--output", type=Path, default=Path("models/escape.json"))
    args = parser.parse_args()
    model = extract(args.data)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(model, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"neurons": len(model["neurons"]), "pairs": len(model["edges"]),
                      "bytes": args.output.stat().st_size, "output": str(args.output)}))


if __name__ == "__main__":
    main()
