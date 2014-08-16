SHELL=/bin/bash
SED?=$(shell which gsed)
SED?=$(shell which sed)

SITEGEN := $(SITEGEN_ROOT)/sitegen.py

.PHONY: help
help:
	@echo Help

.PHONY: deps
deps:
	$(SITEGEN) deps -r .

.PHONY: newmake
newmake:
	$(SITEGEN) make -r .

.PHONY: all
all: _install/.done  _build/.deps

_install/.done: _build/.deps

_install/%.html: _build/%.html templates/current/index.html
	@mkdir -p $(@D)
	@$(SITEGEN) generate -i $< -o $@ -t templates/current -r _install

_build/%.html: source/%.md
	@mkdir -p $(@D)
	@$(SITEGEN) preprocess -i $< -o $@

_install/vendors: vendors
	@mkdir -p $(@D)
	@cp -a $< $@

_install/theme/%: templates/current/assets/%
	@mkdir -p $(@D)
	@echo Copying $<
	@cp -a $< $@

_build/.deps:
	@mkdir -p $(@D)
	@find source -iname '*.md' | $(SED) -E \
	 's#.*source/(.*)\.md#_install/.done: _install/\1.html#' > $@
	@test ! -e vendors || echo '_install/.done: _install/vendors' >> $@
	@find templates/current/assets -type f | $(SED) -E \
	 's#templates/current/assets/(.*)#_install/.done: _install/theme/\1#' >> $@

-include _build/.deps
