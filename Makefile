PVSNESLIB_HOME ?=
SCHISM_HOME ?=
SNES_EMU ?=

.PHONY: all check_required_vars build_venv build test_venv test venv

all: build

check_required_vars:
	@test -n "$(PVSNESLIB_HOME)" || { echo "ERROR: Please create an environment variable PVSNESLIB_HOME by following this guide: https://github.com/alekmaul/pvsneslib/wiki/Installation"; exit 1; }
	@test -n "$(SCHISM_HOME)" || { echo "ERROR: Please create an environment variable SCHISM_HOME by following this guide: :/ sorry, no guide yet"; exit 1; }
	@test -n "$(SNES_EMU)" || { echo "ERROR: Please create an environment variable SNES_EMU by following this guide: :/ sorry, no guide yet"; exit 1; }

venv:
	@if [ "$${OS:-}" = "Windows_NT" ]; then \
		PYCMD=python; \
	else \
		PYCMD=python3; \
	fi; \
	echo "Creating venv with $$PYCMD ..."; \
	$$PYCMD -m venv venv

test_venv: venv
	@if [ "$${OS:-}" = "Windows_NT" ]; then \
		VENVBIN=venv/Scripts; \
	else \
		VENVBIN=venv/bin; \
	fi; \
	$$VENVBIN/pip install -r test/test-requirements.txt

test: check_required_vars test_venv
	@if [ "$${OS:-}" = "Windows_NT" ]; then \
		VENVBIN=venv/Scripts; \
	else \
		VENVBIN=venv/bin; \
	fi; \
	$$VENVBIN/pytest

build_venv: venv
	@if [ "$${OS:-}" = "Windows_NT" ]; then \
		VENVBIN=venv/Scripts; \
	else \
		VENVBIN=venv/bin; \
	fi; \
	$$VENVBIN/pip install -r requirements.txt

build: check_required_vars build_venv
	@if [ "$${OS:-}" = "Windows_NT" ]; then \
		VENVBIN=venv/Scripts; \
	else \
		VENVBIN=venv/bin; \
	fi; \
	$$VENVBIN/flit build
