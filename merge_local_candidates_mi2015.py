#!/usr/bin/env python3

import collections
import re
import utils

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

def merge(tur1, tur2):
    return utils.join_left(tur1, tur2, key, utils.merge_records)

if __name__ == '__main__':
    import sys

    if len(sys.argv) != 3:
        print("Usage: pp_local_candidates.py TUR1_FILE TUR2_FILE",
              file=sys.stderr)
        sys.exit(1)

    tur1 = parse(sys.argv[1])
    tur2 = parse(sys.argv[2])
    records = merge(tur1, tur2)
    utils.write_to_csv(records, sys.stdout)
