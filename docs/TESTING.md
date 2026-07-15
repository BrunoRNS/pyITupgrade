# Testing

This document describes how to run the test suite for `pyIT`, including the integration tests that require external tools.

## Prerequisites

Before running the tests, ensure the following are installed and properly configured:

1. **Python 3.12+** with `pytest` and `mutagen` (they are included in `test-requirements.txt`).
2. **Schism Tracker** – required for the OGG conversion tests.
   - Set the environment variable `SCHISM_HOME` to the directory containing the Schism Tracker executable.
   - On macOS, this should point to the `.app` bundle.
   - On Linux/Windows, point to the folder containing the binary (or the binary itself).
3. **PVSNESlib** – required for the `smconv` tests.
   - Install PVSNESlib following the [official guide](https://github.com/alekmaul/pvsneslib/wiki/Installation).
   - Set `PVSNESLIB_HOME` to the root directory of the PVSNESlib installation.
4. **A SNES emulator** – required for the ROM execution test.
   - Set `SNES_EMU` to the path of your emulator executable (e.g., `snes9x`, `bsnes`).
   - On macOS, this can be an `.app` bundle.

These variables are validated by the Makefile before tests are run.

## Running Tests

### Using the Makefile (Recommended)

The project includes a `Makefile` that automates environment setup and test execution.

1. **Set the required environment variables** (example for Linux/macOS):

   ```bash
   export PVSNESLIB_HOME=/path/to/pvsneslib
   export SCHISM_HOME=/path/to/schism
   export SNES_EMU=/path/to/snes9x
   ```

   For Windows (Command Prompt):

   ```cmd
   set PVSNESLIB_HOME=C:\pvsneslib
   set SCHISM_HOME=C:\schism
   set SNES_EMU=C:\snes9x\snes9x.exe
   ```

2. **Run the tests**:

   ```bash
   make test
   ```

   This command will:
   - Verify that the required environment variables are set.
   - Create a virtual environment (if missing).
   - Install test dependencies (pytest, mutagen, etc.).
   - Execute the test suite with `pytest`.

### Running Tests Manually

If you prefer to run `pytest` directly:

1. Activate your virtual environment.
2. Install test dependencies:

   ```bash
   pip install -r test-requirements.txt
   ```

3. Ensure the environment variables are set (as above).
4. Run:

   ```bash
   pytest
   ```

## Test Structure

The tests are organized in the `test/` directory:

- **`test_assets/`** – verify the built‑in waveform assets are accessible.
- **`test_pattern/`** – unit tests for `PatternBuilder`.
- **`test_tablature/`** – unit tests for `TablatureBuilder`.
- **`test_ogg/`** – integration tests for IT → OGG conversion (requires Schism).
- **`test_smconv/`** – tests for generating SNES soundbanks with `smconv` (requires PVSNESlib).
- **`test_smconv_tablature/`** – same, but using a tablature‑generated IT file.
- **`create_sample_it/`** – helper scripts to create sample IT files for testing.

## Interpreting Test Results

- **Unit tests** (pattern, tablature, assets) should run quickly and are independent of external tools.
- **Integration tests** may take longer and require the external dependencies. If any of the required tools are missing or misconfigured, the tests will fail with clear error messages.

**Note:** The `test_snes_rom` test actually launches an emulator and runs a SNES ROM. This may open a graphical window. Ensure your emulator is configured to run headlessly if you are in a CI environment.

## Skipping Integration Tests

If you lack the external tools, you can skip the integration tests by using `pytest` markers:

```bash
pytest -m "not integration"
```

(You need to define markers in `pytest.ini`; adjust as needed.)
