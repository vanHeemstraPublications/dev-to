# -------------------------------------------
# Prompt Framework Makefile
# -------------------------------------------

PYTHON ?= python3
VENV := .venv
PY := $(VENV)/bin/python
PIP := $(VENV)/bin/pip

SERIES_DIR := series
SERIES_FILES := $(filter-out $(SERIES_DIR)/SERIES_INDEX.yaml,$(wildcard $(SERIES_DIR)/*.yaml))

# Resolve SERIES argument to a YAML path.
# Accepts:
# - SERIES=series/foo.yaml
# - SERIES=foo.yaml          -> series/foo.yaml
# - SERIES=foo               -> series/foo_series.yaml
# - SERIES=foo_series        -> series/foo_series.yaml
define resolve_series
$(if $(findstring /,$(1)),$(1),$(SERIES_DIR)/$(if $(filter %.yaml,$(1)),$(1),$(if $(filter %_series,$(1)),$(1),$(1)_series).yaml))
endef

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

.PHONY: \
	help install lint docs validate check-cli \
	list-series show-series-files \
	generate generate-all generate-series generate-episode \
	generate-image generate-images \
	generate-article generate-articles \
	generate-assets \
	generate-series-cover \
	clean clean-generated

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
	@echo "  make check-cli"
	@echo "      Check prompt-cli.py syntax and basic execution"
	@echo ""
	@echo "Series Discovery"
	@echo "  make list-series"
	@echo "      List all available series from SERIES_INDEX.yaml"
	@echo "  make show-series-files"
	@echo "      Show detected YAML series files in /series"
	@echo ""
	@echo "Prompt Bundles"
	@echo "  make generate SERIES=<your_series>"
	@echo "      Generate prompt bundles for a series"
	@echo "  make generate-series SERIES=series/azure_data_platform.yaml"
	@echo "      Generate all prompt bundles for one series file"
	@echo "  make generate-episode SERIES=azure_data_platform EP=1"
	@echo "      Generate one episode prompt bundle"
	@echo "  make generate-all"
	@echo "      Generate prompt bundles for all series"
	@echo ""
	@echo "Images"
	@echo "  make generate-image SERIES=azure_data_platform EP=1"
	@echo "      Generate one episode banner image"
	@echo "  make generate-images SERIES=azure_data_platform"
	@echo "      Generate all episode banner images for a series"
	@echo "  make generate-series-cover SERIES=azure_data_platform"
	@echo "      Generate a reusable series cover image"
	@echo ""
	@echo "Articles"
	@echo "  make generate-article SERIES=azure_data_platform EP=1"
	@echo "      Generate one article stub"
	@echo "  make generate-articles SERIES=azure_data_platform"
	@echo "      Generate all article stubs for a series"
	@echo ""
	@echo "Convenience"
	@echo "  make generate-assets SERIES=azure_data_platform EP=1"
	@echo "      Generate both the banner image and article stub for one episode"
	@echo ""
	@echo "Maintenance"
	@echo "  make clean-generated"
	@echo "      Remove generated prompt bundles only"
	@echo "  make clean"
	@echo "      Remove generated prompt bundles and the virtual environment"
	@echo ""

install: $(VENV)/bin/activate

lint: $(VENV)/bin/activate
	$(PY) scripts/prompt-lint.py

docs: $(VENV)/bin/activate
	$(PY) scripts/prompt-docs.py

validate: lint docs

check-cli: $(VENV)/bin/activate
	$(PY) -m py_compile scripts/prompt-cli.py
	$(PY) scripts/prompt-cli.py list-series

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

generate: $(VENV)/bin/activate
ifndef SERIES
	$(error SERIES is required. Example: make generate SERIES=azure_data_platform)
endif
	$(PY) scripts/prompt-cli.py generate $(call resolve_series,$(SERIES))

generate-series: $(VENV)/bin/activate
ifndef SERIES
	$(error SERIES is required. Example: make generate-series SERIES=series/azure_data_platform.yaml)
endif
	$(PY) scripts/prompt-cli.py generate $(call resolve_series,$(SERIES))

generate-episode: $(VENV)/bin/activate
ifndef SERIES
	$(error SERIES is required. Example: make generate-episode SERIES=azure_data_platform EP=1)
endif
ifndef EP
	$(error EP is required. Example: make generate-episode SERIES=azure_data_platform EP=1)
endif
	$(PY) scripts/prompt-cli.py generate $(call resolve_series,$(SERIES)) $(EP)

generate-image: $(VENV)/bin/activate
ifndef SERIES
	$(error SERIES is required. Example: make generate-image SERIES=azure_data_platform EP=1)
endif
ifndef EP
	$(error EP is required. Example: make generate-image SERIES=azure_data_platform EP=1)
endif
	$(PY) scripts/prompt-cli.py generate-image $(call resolve_series,$(SERIES)) $(EP)

generate-images: $(VENV)/bin/activate
ifndef SERIES
	$(error SERIES is required. Example: make generate-images SERIES=azure_data_platform)
endif
	$(PY) scripts/prompt-cli.py generate-images $(call resolve_series,$(SERIES))

generate-article: $(VENV)/bin/activate
ifndef SERIES
	$(error SERIES is required. Example: make generate-article SERIES=azure_data_platform EP=1)
endif
ifndef EP
	$(error EP is required. Example: make generate-article SERIES=azure_data_platform EP=1)
endif
	$(PY) scripts/prompt-cli.py generate-article $(call resolve_series,$(SERIES)) $(EP)

generate-articles: $(VENV)/bin/activate
ifndef SERIES
	$(error SERIES is required. Example: make generate-articles SERIES=azure_data_platform)
endif
	$(PY) scripts/prompt-cli.py generate-articles $(call resolve_series,$(SERIES))

generate-assets: $(VENV)/bin/activate
ifndef SERIES
	$(error SERIES is required. Example: make generate-assets SERIES=azure_data_platform EP=1)
endif
ifndef EP
	$(error EP is required. Example: make generate-assets SERIES=azure_data_platform EP=1)
endif
	$(PY) scripts/prompt-cli.py generate-image $(call resolve_series,$(SERIES)) $(EP)
	$(PY) scripts/prompt-cli.py generate-article $(call resolve_series,$(SERIES)) $(EP)

generate-series-cover: $(VENV)/bin/activate
ifndef SERIES
	$(error SERIES is required. Example: make generate-series-cover SERIES=azure_data_platform)
endif
	$(PY) scripts/prompt-cli.py generate-series-cover $(call resolve_series,$(SERIES))

clean-generated:
	rm -rf generated

clean: clean-generated
	rm -rf $(VENV)
