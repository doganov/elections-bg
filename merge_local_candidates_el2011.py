#!/usr/bin/env python3

from collections import namedtuple
import re
import utils

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

def combine_records(variant, candidate, result):
    f = "0"
    if result:
        if result.flag == "И":
            f = "1"
        elif result.flag == "Б":
            f = "2"

    return variant.output(*candidate, flag=f)
    
def combine(variant, candidates_filename, result_filename):
    candidates = parse(candidates_filename, variant.candidate)
    result = parse(result_filename, variant.result)
    return utils.join_left(candidates,
                           result,
                           variant.key,
                           lambda c, r: combine_records(variant, c, r))

def merge(variant, tur1, tur2):
    return utils.join_left(tur1,
                           tur2,
                           variant.key,
                           utils.merge_records)

if __name__ == '__main__':
    import sys

    if len(sys.argv) != 5:
        print("Usage: pp_local_candidates.py TUR1_CANDIDATES_FILE TUR1_RESULTS_FILE TUR2_CANDIDATES_FILE TUR2_RESULTS_FILE",
              file=sys.stderr)
        sys.exit(1)

    variant = detect_variant(sys.argv[1:])
    s1 = combine(variant, *sys.argv[1:3])
    s2 = combine(variant, *sys.argv[3:5])
    records = merge(variant, s1, s2)
    utils.write_to_csv(records, sys.stdout)
