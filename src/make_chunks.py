#!/usr/bin/env python3
"""Generate the canonical download windows.

ENA's Portal API treats `first_public<=E` as EXCLUSIVE of E (verified: a run with
first_public = 2010-10-18 is NOT returned by `>=2010-10-18 AND <=2010-10-18`, but IS returned
by `>=2010-10-18 AND <=2010-10-19`). Windows are therefore expressed as consecutive
boundaries `>=b_i AND <=b_{i+1}`, which partitions the timeline exactly with no gap and no
overlap. Monthly to 2018; 5-day slices from 2019, where monthly responses are large enough
to get truncated in transit."""
import datetime, sys, os
out, d, end = [], datetime.date(2010, 1, 1), datetime.date(2026, 10, 1)
bounds = [datetime.date(1990, 1, 1)]
while d < end:
    y, m = d.year, d.month
    nxt = datetime.date(y + (m == 12), 1 if m == 12 else m + 1, 1)
    if y < 2019:
        bounds.append(d)
    else:
        bounds += [datetime.date(y, m, day) for day in (1, 6, 11, 16, 21, 26)]
    d = nxt
bounds.append(end)
bounds = sorted(set(bounds))
for i in range(len(bounds) - 1):
    out.append(f"w{bounds[i].isoformat()} {bounds[i].isoformat()} {bounds[i+1].isoformat()}")
p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "chunks.txt")
open(p, "w").write("\n".join(out) + "\n")
print(f"{len(out)} half-open windows -> {p}")
