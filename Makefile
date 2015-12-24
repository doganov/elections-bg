SHELL=/bin/sh

PP_LOCAL_CANDIDATES=./pp_local_candidates.py

inputs = mi2015/tur1/$(1)/local_candidates_25.10.2015.txt mi2015/tur2/$(1)/local_candidates_01.11.2015.txt
output = out/$(1)/local_candidates.csv
outputs = $(call output,КК) $(call output,КО) $(call output,КР)

.PHONY: clean

all: $(outputs)

$(outputs): out/%/local_candidates.csv: $(call inputs,%)
	mkdir -p out/$*
	$(PP_LOCAL_CANDIDATES) $+ > $@

clean:
	rm -rf out
