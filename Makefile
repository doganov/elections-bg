SHELL=/bin/sh

MERGE_LOCAL_CANDIDATES_EL2011=./merge_local_candidates_el2011.py
MERGE_LOCAL_CANDIDATES_MI2015=./merge_local_candidates_mi2015.py

variant_bg_el2011 = $(if $(filter КК,$(1)),кмет\ на\ кметство,кмет\ на\ община)
variant_en_el2011 = $(if $(filter КК,$(1)),mrlty,munic)
tur_el2011 = el2011/$(1)/$(call variant_bg_el2011,$(2))/el2011_mayor_$(call variant_en_el2011,$(2))_candidates.txt el2011/$(1)/$(call variant_bg_el2011,$(2))/el2011_mayor_$(call variant_en_el2011,$(2))_result.txt
inputs_el2011 = $(call tur_el2011,t1,$(1)) $(call tur_el2011,t2,$(1))
output_el2011 = out/2011/$(1)/local_candidates.csv
outputs_el2011 = $(call output_el2011,КК) $(call output_el2011,КО)

inputs_mi2015 = mi2015/tur1/$(1)/local_candidates_25.10.2015.txt mi2015/tur2/$(1)/local_candidates_01.11.2015.txt
output_mi2015 = out/2015/$(1)/local_candidates.csv
outputs_mi2015 = $(call output_mi2015,КК) $(call output_mi2015,КО) $(call output_mi2015,КР)

.PHONY: clean

all: $(outputs_el2011) $(outputs_mi2015)

$(call output_el2011,КК): $(call inputs_el2011,КК)
	mkdir -p out/2011/КК
	$(MERGE_LOCAL_CANDIDATES_EL2011) $(call inputs_el2011,КК) > $@

$(call output_el2011,КО): $(call inputs_el2011,КО)
	mkdir -p out/2011/КО
	$(MERGE_LOCAL_CANDIDATES_EL2011) $(call inputs_el2011,КО) > $@

$(outputs_mi2015): out/2015/%/local_candidates.csv: $(call inputs_mi2015,%)
	mkdir -p out/2015/$*
	$(MERGE_LOCAL_CANDIDATES_MI2015) $+ > $@

clean:
	rm -rf out
