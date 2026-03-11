PYTHON ?= python

PYTHON_SERIES := series/python_story_series.yaml
KUBERNETES_SERIES := series/container_harbour_series.yaml

.PHONY: help install lint docs list-series generate-python generate-kubernetes generate-kubernetes-episode-4 validate clean

help:
	@echo "Available commands:"
	@echo "  make install                    Install Python dependencies"
	@echo "  make lint                       Validate prompt framework files"
	@echo "  make docs                       Regenerate docs/EPISODE_INDEX.md and docs/SERIES_INDEX.md"
	@echo "  make list-series                List all available series"
	@echo "  make generate-python            Generate all prompt bundles for the Python series"
	@echo "  make generate-kubernetes        Generate all prompt bundles for the Kubernetes series"
	@echo "  make generate-kubernetes-episode-4  Generate only Kubernetes episode 4"
	@echo "  make validate                   Run lint + docs generation"
	@echo "  make clean                      Remove generated prompt bundles"

install:
	$(PYTHON) -m pip install -r requirements.txt

lint:
	$(PYTHON) scripts/prompt-lint.py

docs:
	$(PYTHON) scripts/prompt-docs.py

list-series:
	$(PYTHON) scripts/prompt-cli.py list-series

generate-python:
	$(PYTHON) scripts/prompt-cli.py generate $(PYTHON_SERIES)

generate-kubernetes:
	$(PYTHON) scripts/prompt-cli.py generate $(KUBERNETES_SERIES)

generate-kubernetes-episode-4:
	$(PYTHON) scripts/prompt-cli.py generate $(KUBERNETES_SERIES) 4

validate: lint docs

clean:
	rm -rf generated