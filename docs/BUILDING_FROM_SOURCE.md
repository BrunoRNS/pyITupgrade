# Building from Source

This guide explains how to build the `pyITupgrade` library from source, including setting up the development environment and generating distribution packages.

## Prerequisites

- **Python 3.10 or newer**  
  Ensure `python` (or `python3`) is available in your PATH.
- **Git** – to clone the repository.
- **A working C compiler** (optional) – only needed if any dependencies require compilation (e.g., `numpy`, `scipy`). On most platforms, pre‑built wheels are available.

## Step 1: Clone the Repository

```bash
git clone https://github.com/BrunoRNS/pyITupgrade.git
cd pyITupgrade
```

## Step 2: Create a Virtual Environment (Recommended)

Create and activate a virtual environment to isolate the build environment:

```bash
python -m venv venv
source venv/bin/activate        # On Linux/macOS
# or
venv\Scripts\activate           # On Windows
```

## Step 3: Install Build Tools and Dependencies

Install the runtime dependencies and the build tools:

```bash
pip install -r requirements.txt
pip install build   # optional, but recommended
```

The `requirements.txt` file includes `numpy`, `scipy`, `pydub`, and other runtime libraries.  
The `build` package is used to create distribution packages.

## Step 4: Build the Distribution Package

Use the standard Python build tool:

```bash
python -m build
```

This will produce a wheel (`.whl`) and a source distribution (`.tar.gz`) inside the `dist/` directory:

```sh
dist/
├── pyITupgrade-<version>-py3-none-any.whl
└── pyITupgrade-<version>.tar.gz
```

## Step 5: Install the Built Package (Optional)

You can install the freshly built wheel into your environment for testing:

```bash
pip install dist/pyITupgrade-*.whl
```

Alternatively, you can install the package in **editable mode** for development:

```bash
pip install -e .
```

## Step 6: Verify the Installation

Run a quick sanity check:

```bash
python -c "import pyIT; print(pyIT.__version__)"
```

If no error occurs, the build succeeded.

## Troubleshooting

- **Missing `build` tool**: Install it with `pip install build`.
- **Permission errors**: On Unix‑like systems, you may need to use `sudo` for system‑wide installs, but we recommend using a virtual environment to avoid that.
- **Dependency build failures**: On some platforms (e.g., ARM, older macOS), `numpy`/`scipy` might require a compiler. Install the appropriate development tools (e.g., `build-essential` on Debian, Xcode on macOS) and try again.
- **Import error `No module named 'pyIT'`**: Make sure you have installed the package correctly (`pip install -e .` or `pip install dist/*.whl`). The import name is `pyIT` (not `pyITupgrade`).

## Additional Makefile Targets

If you are using the provided `Makefile`, you can simply run:

```bash
make build
```

This will:

- Check required environment variables (`PVSNESLIB_HOME`, `SCHISM_HOME`, `SNES_EMU`).
- Create a virtual environment.
- Install runtime dependencies.
- Build the distribution packages.

For testing, run:

```bash
make test
```

Which will install test dependencies and run the test suite.

## Publishing to PyPI

After building the packages, you can upload them to PyPI using `twine`:

```bash
pip install twine
twine upload dist/*
```

Make sure you have configured the project name (`pyITupgrade`) correctly in `pyproject.toml` and that the package already exists on PyPI.
