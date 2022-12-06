# Constants
DATA_DIR := data
TREC_EVAL_BIN:=./trec_eval
SUPP_DIR := ./supplementary

# Getting cross product all targets
all_modes := train test
ifdef mode
	all_modes := $(mode)
endif

all_lans := cs en
ifdef lan
	all_lans := $(lan)
endif

# Default values
run ?= run-0

.PHONY: eval res all report beamer supplementary

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

all_eval_files = $(wildcard evals/*.eval)
supplementary: $(all_eval_files)
	python scripts/table.py -i ./evals/run-0_*.eval -o $(SUPP_DIR)/table_run-0.tex
	python scripts/graph.py -i ./evals/run-0_*.eval -o $(SUPP_DIR)/graph_run-0.png
	python scripts/table.py -i ./evals/run-0_*.eval ./evals/run-0-tfidf_*.eval -o $(SUPP_DIR)/table_run-0-tfidf.tex
	python scripts/graph.py -i ./evals/run-0_*.eval ./evals/run-0-tfidf_*.eval -o $(SUPP_DIR)/graph_run-0-tfidf.png
	python scripts/table.py -i ./evals/run-0-tfidf_*.eval ./evals/run-0-sep-*.eval -o $(SUPP_DIR)/table_run-0-sep.tex
	python scripts/graph.py -i ./evals/run-0-tfidf_*.eval ./evals/run-0-sep-*.eval -o $(SUPP_DIR)/graph_run-0-sep.png
	python scripts/table.py -i ./evals/run-0-sep-quot-par_*.eval ./evals/run-0-stopwords-*.eval -o $(SUPP_DIR)/table_run-0-stopwords.tex
	python scripts/graph.py -i ./evals/run-0-sep-quot-par_*.eval ./evals/run-0-stopwords-*.eval -o $(SUPP_DIR)/graph_run-0-stopwords.png
	python scripts/table.py -i ./evals/run-0-stopwords-600_cs.eval ./evals/run-0-stopwords-kaggle_en.eval ./evals/run-0-tagblacklist_*.eval -o $(SUPP_DIR)/table_run-0-tagblacklist.tex
	python scripts/graph.py -i ./evals/run-0-stopwords-600_cs.eval ./evals/run-0-stopwords-kaggle_en.eval ./evals/run-0-tagblacklist_*.eval -o $(SUPP_DIR)/graph_run-0-tagblacklist.png

all_report_files = $(wildcard report/*.tex)
report: $(all_report_files)
	pdflatex -output-directory report $(all_report_files)
	pdflatex -output-directory report $(all_report_files)

all_beamer_files = $(wildcard beamer/*.tex)
beamer: $(all_beamer_files)
	pdflatex -output-directory beamer $(all_beamer_files)
	pdflatex -output-directory beamer $(all_beamer_files)

solution.zip:
	zip solution.zip -r ./main.py ./src/ ./Makefile ./requirements.txt ./scripts/ ./stopwords/ ./beamer/doc.pdf ./report/doc.pdf ./evals/ ./res/
	zip solution.zip -d \*/__pycache__\* \*/__pycache__\*
