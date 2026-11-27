#!/usr/bin/env python3
import csv
import os
import subprocess
import sys
import tomllib

with open("brench.toml", "rb") as config:
    runs = list(tomllib.load(config)["runs"])

row_format = "{:<28}" + "  {:>10}" * len(runs)
print(row_format.format("case", *runs), flush=True)

with subprocess.Popen(
    ["brench", "brench.toml", *sys.argv[1:]],
    stdout=subprocess.PIPE,
    text=True,
    env={**os.environ, "PYTHONUNBUFFERED": "1"},
) as brench:
    results: list[str] = []
    printed_case = False
    for row in csv.DictReader(brench.stdout):
        results.append(row["result"])
        if len(results) == len(runs):
            print(row_format.format(row["benchmark"], *results), flush=True)
            results.clear()
            printed_case = True

    status = brench.wait()
    if status:
        sys.exit(status)
    if not printed_case:
        sys.exit("No benchmarks were run.")
