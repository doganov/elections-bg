SHELL=/bin/sh

MERGE_LOCAL_CANDIDATES_MI2015=./merge_local_candidates_mi2015.py

inputs_mi2015 = mi2015/tur1/$(1)/local_candidates_25.10.2015.txt mi2015/tur2/$(1)/local_candidates_01.11.2015.txt
output_mi2015 = out/$(1)/local_candidates.csv
outputs_mi2015 = $(call output_mi2015,КК) $(call output_mi2015,КО) $(call output_mi2015,КР)

.PHONY: clean

all: $(outputs_mi2015)

$(outputs_mi2015): out/%/local_candidates.csv: $(call inputs_mi2015,%)
	mkdir -p out/$*
	$(MERGE_LOCAL_CANDIDATES_MI2015) $+ > $@

clean:
	rm -rf out
