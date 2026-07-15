# Building from Source

This guide explains how to build the `pyIT` library from source, including setting up the development environment and generating distribution packages.

## Prerequisites

- **Python 3.10 or newer**  
  Ensure `python` (or `python3`) is available in your PATH.
- **Git** – to clone the repository.
- **A working C compiler** (optional) – only needed if any dependencies require compilation (e.g., `numpy`, `scipy`). On most platforms, pre‑built wheels are available.

## Step 1: Clone the Repository

```bash
git clone https://github.com/BrunoRNS/homebrew-renpylib.git
cd homebrew-renpylib
```

_(Adjust the repository URL if it differs.)_

## Step 2: Create a Virtual Environment (Recommended)

Create and activate a virtual environment to isolate the build environment:

```bash
python -m venv venv
source venv/bin/activate        # On Linux/macOS
# or
venv\Scripts\activate           # On Windows
```

## Step 3: Install Build Tools and Dependencies

Install `flit` (the build backend) and the runtime dependencies:

```bash
pip install -r requirements.txt
```

This installs `flit` itself, plus `numpy`, `scipy`, `pydub`, and `scipy-stubs`.

## Step 4: Build the Distribution Package

Use `flit` to build a wheel and a source distribution:

```bash
flit build
```

After a successful build, you will find the packages in the `dist/` directory:

```sh
dist/
├── pyIT-<version>-py3-none-any.whl
└── pyIT-<version>.tar.gz
```

## Step 5: Install the Built Package (Optional)

You can install the freshly built wheel into your environment for testing:

```bash
pip install dist/pyIT-*.whl
```

## Step 6: Verify the Installation

Run a quick sanity check:

```python
python -c "import pyIT; print(pyIT.__version__)"
```

If no error occurs, the build succeeded.

## Troubleshooting

- **Missing `flit`**: Ensure `flit` is installed (`pip install flit`).
- **Permission errors**: On Unix‑like systems, you may need to use `sudo` for system‑wide installs, but we recommend using a virtual environment to avoid that.
- **Dependency build failures**: On some platforms (e.g., ARM, older macOS), `numpy`/`scipy` might require a compiler. Install the appropriate development tools (e.g., `build-essential` on Debian, Xcode on macOS) and try again.
