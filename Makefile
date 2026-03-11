# -------------------------------------------
# Prompt Framework Makefile
# -------------------------------------------

PYTHON ?= python3
VENV := .venv
PY := $(VENV)/bin/python
PIP := $(VENV)/bin/pip

SERIES_DIR := series
SERIES_FILES := $(filter-out $(SERIES_DIR)/SERIES_INDEX.yaml,$(wildcard $(SERIES_DIR)/*.yaml))

# -------------------------------------------
# Internal helper
# -------------------------------------------

$(VENV)/bin/activate:
	$(PYTHON) -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt

# -------------------------------------------
# Commands
# -------------------------------------------

.PHONY: help install lint docs list-series generate-all generate-series generate-episode validate clean show-series-files

help:
	@echo ""
	@echo "Prompt Framework Commands"
	@echo ""
	@echo "Setup"
	@echo "  make install"
	@echo "      Create virtual environment and install dependencies"
	@echo ""
	@echo "Validation"
	@echo "  make lint"
	@echo "      Validate prompt framework files"
	@echo "  make docs"
	@echo "      Regenerate docs/EPISODE_INDEX.md and docs/SERIES_INDEX.md"
	@echo "  make validate"
	@echo "      Run lint + docs"
	@echo ""
	@echo "Series"
	@echo "  make list-series"
	@echo "      List all available series from SERIES_INDEX.yaml"
	@echo "  make show-series-files"
	@echo "      Show detected YAML series files in /series"
	@echo "  make generate-all"
	@echo "      Generate prompt bundles for all detected series files"
	@echo "  make generate-series SERIES=series/python_story_series.yaml"
	@echo "      Generate all prompt bundles for one series file"
	@echo "  make generate-episode SERIES=series/container_harbour_series.yaml EP=4"
	@echo "      Generate one episode from one series file"
	@echo ""
	@echo "Maintenance"
	@echo "  make clean"
	@echo "      Remove generated files and virtual environment"
	@echo ""

install: $(VENV)/bin/activate

lint: $(VENV)/bin/activate
	$(PY) scripts/prompt-lint.py

docs: $(VENV)/bin/activate
	$(PY) scripts/prompt-docs.py

validate: lint docs

list-series: $(VENV)/bin/activate
	$(PY) scripts/prompt-cli.py list-series

show-series-files:
	@echo "Detected series files:"
	@for file in $(SERIES_FILES); do echo "  $$file"; done

generate-all: $(VENV)/bin/activate
	@for file in $(SERIES_FILES); do \
		echo "Generating prompt bundles for $$file"; \
		$(PY) scripts/prompt-cli.py generate $$file || exit 1; \
	done

generate-series: $(VENV)/bin/activate
ifndef SERIES
	$(error SERIES is required. Example: make generate-series SERIES=series/python_story_series.yaml)
endif
	$(PY) scripts/prompt-cli.py generate $(SERIES)

generate-episode: $(VENV)/bin/activate
ifndef SERIES
	$(error SERIES is required. Example: make generate-episode SERIES=series/container_harbour_series.yaml EP=4)
endif
ifndef EP
	$(error EP is required. Example: make generate-episode SERIES=series/container_harbour_series.yaml EP=4)
endif
	$(PY) scripts/prompt-cli.py generate $(SERIES) $(EP)

check-cli:
	$(PY) -m py_compile scripts/prompt-cli.py
	$(PY) scripts/prompt-cli.py list-series

clean:
	rm -rf generated
	rm -rf $(VENV)