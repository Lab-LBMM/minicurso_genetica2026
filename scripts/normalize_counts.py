#!/usr/bin/env python3
"""
normalize_counts.py

Expected fields (tab-separated):
Date    Site    Colony  Local   Caste   No_ants No_parasitized_ants     A_attophilus    A_vicosae        N_erthali        M_grandicornis

This script parses arguments, reads the TSV into a pandas DataFrame and
validates that the required columns are present. Further metric computations
will be added later.
"""

import argparse
import sys

p = argparse.ArgumentParser(
    prog="normalize_counts.py",
    description="Load  TSV of ant colony counts.",
)
p.add_argument("--input", required=True, type=str, help="TSV file (tab-separated)")
p.add_argument("-d", "--delimiter", default="\t", help="Field delimiter (default: tab)")

args = p.parse_args()

parasites_trail_soldiers = {"PAL": {"total": 0,
                            "a_attophilus": 0,
                            "a_vicosae": 0,
                            "n_erthali": 0,
                            "m_grandicornis": 0},
                            "EMB": {"total": 0,
                            "a_attophilus": 0,
                            "a_vicosae": 0,
                            "n_erthali": 0,
                            "m_grandicornis": 0},
                            "UFT": {"total": 0,
                            "a_attophilus": 0,
                            "a_vicosae": 0,
                            "n_erthali": 0,
                            "m_grandicornis": 0},}

parasites_trail_workers = {"PAL": {"total": 0,
                            "a_attophilus": 0,
                            "a_vicosae": 0,
                            "n_erthali": 0,
                            "m_grandicornis": 0},
                            "EMB": {"total": 0,
                            "a_attophilus": 0,
                            "a_vicosae": 0,
                            "n_erthali": 0,
                            "m_grandicornis": 0},
                            "UFT": {"total": 0,
                            "a_attophilus": 0,
                            "a_vicosae": 0,
                            "n_erthali": 0,
                            "m_grandicornis": 0},}

with open(args.input, "r", encoding="utf-8") as fh:
    for line in fh:
        if not line.strip():
            continue
        # skip header if present
        if line.lstrip().startswith("Date\t"):
            continue

        parts = line.rstrip("\n").split("\t")
        if len(parts) < 11:
            # malformed line; skip
            continue
        date, site, colony, local, caste, no_ants, no_parasitized_ants, a_attophilus, a_vicosae, n_erthali, m_grandicornis = parts[:11]

        # convert numeric fields
        try:
            no_ants = int(no_ants)
            no_parasitized_ants = int(no_parasitized_ants)
            a_attophilus = int(a_attophilus)
            a_vicosae = int(a_vicosae)
            n_erthali = int(n_erthali)
            m_grandicornis = int(m_grandicornis)
        except ValueError:
            # skip lines with non-integer counts
            continue
        
        if local != "trail":
            continue

        # choose target dict by caste (soldiers vs workers)
        if str(caste).strip().lower().startswith("s"):
            target = parasites_trail_soldiers
        else:
            target = parasites_trail_workers

        # accumulate counts for the site if recognized
        if site in target:
            target[site]["total"] += no_ants
            target[site]["a_attophilus"] += a_attophilus
            target[site]["a_vicosae"] += a_vicosae
            target[site]["n_erthali"] += n_erthali
            target[site]["m_grandicornis"] += m_grandicornis

for site in parasites_trail_soldiers.keys():
    total_parasited_soldiers = parasites_trail_soldiers[site]["a_attophilus"] + parasites_trail_soldiers[site]["a_vicosae"] + \
        parasites_trail_soldiers[site]["n_erthali"] + parasites_trail_soldiers[site]["m_grandicornis"]
    for parasite in ["a_attophilus", "a_vicosae", "n_erthali", "m_grandicornis"]:
        print(f"{site}_trail_soldiers\t{parasite}\t{parasites_trail_soldiers[site]["total"]}\t{parasites_trail_soldiers[site][parasite]}\t{(parasites_trail_soldiers[site][parasite] / parasites_trail_soldiers[site]["total"]) * 100}\t{(parasites_trail_soldiers[site][parasite] / total_parasited_soldiers) * 100}")

for site in parasites_trail_workers.keys():
    total_parasited_workers = parasites_trail_workers[site]["a_attophilus"] + parasites_trail_workers[site]["a_vicosae"] + \
        parasites_trail_workers[site]["n_erthali"] + parasites_trail_workers[site]["m_grandicornis"]
    for parasite in ["a_attophilus", "a_vicosae", "n_erthali", "m_grandicornis"]:
        print(f"{site}_trail_workers\t{parasite}\t{parasites_trail_workers[site]["total"]}\t{parasites_trail_workers[site][parasite]}\t{(parasites_trail_workers[site][parasite] / parasites_trail_workers[site]["total"]) * 100}\t{(parasites_trail_workers[site][parasite] / total_parasited_workers) * 100}")