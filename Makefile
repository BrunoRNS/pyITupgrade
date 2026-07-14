PVSNESLIB_HOME ?=
SCHISM_HOME ?=
SNES_EMU ?=

ifeq ($(strip $(PVSNESLIB_HOME)),)
$(error "Please create an environment variable PVSNESLIB_HOME by following this guide: https://github.com/alekmaul/pvsneslib/wiki/Installation")
endif

ifeq ($(strip $(SCHISM_HOME)),)
$(error "Please create an environment variable SCHISM_HOME by following this guide: :/ sorry, no guide yet")
endif

ifeq ($(strip $(SNES_EMU)),)
$(error "Please create an environment variable SNES_EMU by following this guide: :/ sorry, no guide yet")
endif

venv:
	python3 -m venv venv

test_venv: venv
	. venv/bin/activate
	pip install -r test/test-requirements.txt

test: test_venv
	pytest

build_venv: venv
	. venv/bin/activate
	pip install -r requirements.txt

build: build_venv
	flit build

.PHONY: build_venv build test_venv test all

all: build
