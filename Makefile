# Constants
DATA_DIR = data
TREC_EVAL_BIN=./trec_eval

# Getting cross product all targets
all_modes = train test
ifdef $(mode)
	all_modes = $(mode)
endif

all_lans = cs en
ifdef $(lan)
	all_modes = $(lan)
endif

# Default values
run ?= run-0

.PHONY: eval res all

$(run)_cs.eval: $(run)_train_cs.res
	$(TREC_EVAL_BIN) -M1000 $(DATA_DIR)/qrels-train_cs.txt $(run)_train_cs.res > $@

$(run)_en.eval: $(run)_train_en.res
	$(TREC_EVAL_BIN) -M1000 $(DATA_DIR)/qrels-train_en.txt $(run)_train_en.res > $@

$(run)_train_cs.res:
	python main.py -q $(DATA_DIR)/topics-train_cs.xml -d $(DATA_DIR)/documents_cs.lst -r $(run)_cs -o $@

$(run)_train_en.res:
	python main.py -q $(DATA_DIR)/topics-train_en.xml -d $(DATA_DIR)/documents_en.lst -r $(run)_en -o $@

$(run)_test_cs.res:
	python main.py -q $(DATA_DIR)/topics-test_cs.xml -d $(DATA_DIR)/documents_cs.lst -r $(run)_cs -o $@

$(run)_test_en.res:
	python main.py -q $(DATA_DIR)/topics-test_en.xml -d $(DATA_DIR)/documents_en.lst -r $(run)_en -o $@

eval: $(foreach lan,$(all_lans),$(run)_$(lan).eval)

res: $(foreach lan,$(all_lans),$(foreach mode,$(all_modes),$(run)_$(mode)_$(lan).res))

pdf: $(wildcard report/*.tex)
	pdflatex -output-directory report $^
