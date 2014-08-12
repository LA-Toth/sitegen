SHELL=/bin/bash
PAGES=
SED?=$(shell which gsed)
SED?=$(shell which sed)

.PHONY: help
help:
	@echo Help

.PHONY: all
all: _install/.done  _build/.deps

_install/.done: _build/.deps

_install/%.html: _build/%.html templates/current/index.html
	@mkdir -p $(@D)
	@$(SITEGEN_ROOT)/sitegen.py generate -i $< -o $@ -t templates/current

_build/%.html: source/%.md
	@mkdir -p $(@D)
	@python -m markdown -o html5 -f $@ $<

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
	 's#.*source/(.*)\.md#PAGES += &\n_build/.pages.deps: &\n_install/.done: _install/\1.html#' > $@
	@test ! -e vendors || echo '_install/.done: _install/vendors' >> $@
	@find templates/current/assets -type f | $(SED) -E \
	 's#templates/current/assets/(.*)#_build/.templates.deps: &\n_install/.done: _install/theme/\1#' >> $@

-include _build/.deps
