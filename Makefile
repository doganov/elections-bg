SHELL=/bin/sh

MERGE_LOCAL_CANDIDATES_MI2015=./merge_local_candidates_mi2015.py

inputs = mi2015/tur1/$(1)/local_candidates_25.10.2015.txt mi2015/tur2/$(1)/local_candidates_01.11.2015.txt
output = out/$(1)/local_candidates.csv
outputs = $(call output,КК) $(call output,КО) $(call output,КР)

.PHONY: clean

all: $(outputs)

$(outputs): out/%/local_candidates.csv: $(call inputs,%)
	mkdir -p out/$*
	$(MERGE_LOCAL_CANDIDATES_MI2015) $+ > $@

clean:
	rm -rf out
