.PHONY: build check contract-test lint root-test test verify
.SECONDEXPANSION:

override SHELL := /bin/sh
override .SHELLFLAGS := -c
ifneq ($(strip $(MAKEFILES)),)
$(error MAKEFILES must be empty; repository verification requires this Makefile to be loaded alone)
endif
override MAKEFILES :=
ifneq ($(origin MAKEFILE_LIST),file)
$(error MAKEFILE_LIST must not be overridden)
endif
override ROOT := $(shell sed_path=/usr/bin/sed; [ -x "$$sed_path" ] || sed_path=/bin/sed; [ -x "$$sed_path" ] || exit 1; path=$$(printf '%s' '$(subst ','"'"',$(MAKEFILE_LIST))' | "$$sed_path" 's/^ //'); [ -f "$$path" ] || exit 1; directory=$${path%/*}; [ "$$directory" != "$$path" ] || directory=.; CDPATH= cd "$$directory" && pwd -P)
export ROOT
ifeq ($(strip $(ROOT)),)
$(error repository Makefile path could not be resolved)
endif
build check contract-test lint root-test test verify: $$(if $$(filter file,$$(origin MAKEFILE_LIST)),,$$(error MAKEFILE_LIST must not be overridden))
build check contract-test lint root-test test verify: $$(if $$(shell sed_path=/usr/bin/sed && [ -x "$$$$sed_path" ] || sed_path=/bin/sed && [ -x "$$$$sed_path" ] && path=$$$$(printf '%s' '$$(subst ','"'"',$$(MAKEFILE_LIST))' | "$$$$sed_path" 's/^ //') && [ -f "$$$$path" ] && printf '%s' ok),,$$(error repository Makefile must be loaded alone))

PYTHON ?= python2
ifneq ($(words $(value PYTHON)),1)
$(error PYTHON must be exactly python2 or python3)
endif
ifeq ($(filter python2 python3,$(value PYTHON)),)
$(error PYTHON must be exactly python2 or python3)
endif
override PYTHON := $(value PYTHON)
override PYTHONDONTWRITEBYTECODE := 1
export PYTHONDONTWRITEBYTECODE

lint:
	$(PYTHON) -B "$$ROOT/scripts/check-docs-plans.py"
	cd "$$ROOT" && $(PYTHON) -B -c 'compile(open("scrape.py").read(), "scrape.py", "exec")'

contract-test:
	$(PYTHON) -B "$$ROOT/scripts/test_workflow_contract.py"

test:
	cd "$$ROOT" && $(PYTHON) -B -m unittest discover -s tests

build: lint

root-test:
	/bin/sh "$$ROOT/scripts/test-makefile-root.sh"

verify: root-test lint contract-test test

check: verify
