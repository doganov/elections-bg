#!/usr/bin/env python3

import csv
import collections
import re

#   1) Код на ОИК
#   2) Наименование на Община/Кметство/Район
#   3) Номер на партия/коалиция/инициативен комитет
#   4) Име на партия/коалиция/инициативен комитет
#   5) Номер на кандидат в листата
#   6) Име на кандидат
#   7) Флаг за избран кандидат(0-не е избран, 1-избран, 2-балотаж)

Record = collections.namedtuple("Record",
                                ("code",
                                 "place_name",
                                 "party_no",
                                 "party_name",
                                 "cand_no",
                                 "cand_name",
                                 "flag"))

RECORD_RE = re.compile(r"([0-9]+);([^;]+);([0-9]+);(.+);([0-9]+);([^;]+);([012])")

def key(rec):
    return (rec.code, rec.place_name, rec.party_no, rec.cand_no)

def parse(filename):
    with open(filename) as f:
        return [Record._make(RECORD_RE.match(line).groups()) for line in f]

def merge_records(rec1, rec2):
    if rec1.flag == "1":
        if rec2:
            raise ValueError("Found record in TUR2 where none is expected: " + str(rec2))
        return rec1

    if (rec1.flag == "2") and (not rec2):
        # Sometimes a candidate is eligible to go to TUR2, but gives up
        return rec1._replace(flag="0")

    if not rec2:
        return rec1

    f = rec2.flag
    if f == "0":
        f = "2"
    elif f == "1":
        f = "3"
    else:
        f = "?"

    return rec1._replace(flag=f)

def merge(tur1, tur2):
    t1 = parse(tur1)
    t2 = parse(tur2)

    t2_pool = {key(rec): rec for rec in t2}

    merged = [merge_records(rec, t2_pool.get(key(rec))) for rec in t1]
    
    s1 = set((key(rec) for rec in t1))
    s2 = set((key(rec) for rec in t2))

    leftovers = s2 - s1
    if len(leftovers) > 0:
        raise ValueError("Canidates on TUR2 that were not on TUR1: " + leftovers)

    return merged

def write_to_csv(recs, out):
    writer = csv.writer(out, delimiter="|")
    writer.writerows(recs)

if __name__ == '__main__':
    import sys

    if len(sys.argv) != 3:
        print("Usage: pp_local_candidates.py TUR1_FILE TUR2_FILE",
              file=sys.stderr)
        sys.exit(1)
    
    records = merge(*sys.argv[1:])
    write_to_csv(records, sys.stdout)
