import csv

def join_left(seq1, seq2, keyf, f):
    seq2_pool = {keyf(rec): rec for rec in seq2}
    joined = [f(rec, seq2_pool.get(keyf(rec))) for rec in seq1]

    s1 = set((keyf(rec) for rec in seq1))
    s2 = set((keyf(rec) for rec in seq2))

    leftovers = s2 - s1
    if len(leftovers) > 0:
        raise ValueError("SEQ2 is not consumed completely: " + leftovers)

    return joined

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

def write_to_csv(recs, out):
    writer = csv.writer(out, delimiter="|")
    writer.writerows(recs)
