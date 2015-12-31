#!/usr/bin/env python3

import csv
from collections import namedtuple
import re

Variant = namedtuple("Variant",
                     ("candidate",
                      "result",
                      "output",
                      "key"))

#   1) Код на ОИК
#   2) ЕКАТТЕ на кметство
#   3) Име на кметство
#   4) Номер на партията/коалицията/инициативния комитет, издигнал кандидата 
#   5) Име на кандидата

MrltyCandidate = namedtuple("MrltyCandidate",
                            ("code",
                             "mrlty_no",                                      
                             "mrlty_name",
                             "party_no",
                             "cand_name"))

# По документация:
#
#   1) Това поле показва дали кандидатът е избран или отива на балотаж
#   2) код на ОИК;
#   3) Община;
#   4) Код на кметство;
#   5) кметство;
#   6) Номер на партия/коалиция;
#   7) Име на кандидат
#   8) Брой гласове за кандидата
#
# В действителност:
#
#   1) Това поле показва дали кандидатът е избран или отива на балотаж
#   2) код на ОИК;
#   3) Община;
#   4) Код на кметство;
#   5) Име на кандидат
#   6) Номер на партия/коалиция;
#   7) кметство;
#   8) Брой гласове за кандидата

MrltyResult = namedtuple("MrltyResult",
                         ("flag",
                          "code",
                          "munic_name",
                          "mrlty_no",
                          "cand_name",
                          "party_no",
                          "mrlty_name",
                          "votes"))

MrltyOutput = namedtuple("MrltyOutput", MrltyCandidate._fields + ("flag",))

MrltyVariant = Variant(
    MrltyCandidate,
    MrltyResult,
    MrltyOutput,
    lambda rec: (rec.code, rec.mrlty_no, rec.party_no))

#   1) Код на ОИК
#   2) Номер на партията/коалицията/инициативния комитет, издигнал кандидата 
#   3) Име на кандидата

MunicCandidate = namedtuple("MunicCandidate",
                            ("code",
                             "party_no",
                             "cand_name"))

#   1) Това поле показва дали кандидатът е избран или отива на балотаж
#   2) код на ОИК;
#   3) Община;
#   4) Номер на партия/коалиция;
#   5) Име на кандидат
#   6) Брой гласове за кандидата

MunicResult = namedtuple("MunicResult",
                         ("flag",
                          "code",
                          "place_name",
                          "party_no",                                            
                          "cand_name",
                          "votes"))

MunicOutput = namedtuple("MunicOutput", MunicCandidate._fields + ("flag",))

MunicVariant = Variant(
    MunicCandidate,
    MunicResult,
    MunicOutput,
    lambda rec: (rec.code, rec.party_no))

def detect_variant(filenames):
    if all(["_mrlty_" in f for f in filenames]):
        return MrltyVariant
    if all(["_munic_" in f for f in filenames]):
        return MunicVariant

    raise ValueError("Can not deduce variant from filenames: " + str(filenames))

def parse(filename, recordType):
    with open(filename) as f:
        return [recordType._make(line.strip().split(";")) for line in f]

def combine_left(seq1, seq2, keyf, f):
    seq2_pool = {keyf(rec): rec for rec in seq2}
    combined = [f(rec, seq2_pool.get(keyf(rec))) for rec in seq1]

    s1 = set((keyf(rec) for rec in seq1))
    s2 = set((keyf(rec) for rec in seq2))

    leftovers = s2 - s1
    if len(leftovers) > 0:
        raise ValueError("SEQ2 is not consumed completely: " + leftovers)

    return combined

def join_records(variant, candidate, result):
    f = "0"
    if result:
        if result.flag == "И":
            f = "1"
        elif result.flag == "Б":
            f = "2"

    return variant.output(*candidate, flag=f)
    
def join(variant, candidates_filename, result_filename):
    candidates = parse(candidates_filename, variant.candidate)
    result = parse(result_filename, variant.result)
    return combine_left(candidates,
                        result,
                        variant.key,
                        lambda c, r: join_records(variant, c, r))

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

def merge(variant, tur1, tur2):
    return combine_left(tur1,
                        tur2,
                        variant.key,
                        merge_records)

def write_to_csv(recs, out):
    writer = csv.writer(out, delimiter="|")
    writer.writerows(recs)

if __name__ == '__main__':
    import sys

    if len(sys.argv) != 5:
        print("Usage: pp_local_candidates.py TUR1_CANDIDATES_FILE TUR1_RESULTS_FILE TUR2_CANDIDATES_FILE TUR2_RESULTS_FILE",
              file=sys.stderr)
        sys.exit(1)

    variant = detect_variant(sys.argv[1:])
    s1 = join(variant, *sys.argv[1:3])
    s2 = join(variant, *sys.argv[3:5])
    records = merge(variant, s1, s2)
    write_to_csv(records, sys.stdout)
