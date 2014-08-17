SHELL=/bin/bash
SED?=$(shell which gsed)
SED?=$(shell which sed)

SITEGEN := $(SITEGEN_ROOT)/sitegen.py

.PHONY: help
help:
	@echo Available targets:
	@echo
	@echo "all   - Generate site"
	@echo "deps  - List dependencies and actions for debugging"

.PHONY: deps
deps:
	@$(SITEGEN) deps -r .

.PHONY: all
all:
	@$(SITEGEN) make -r .
