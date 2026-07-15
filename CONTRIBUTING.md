# Contributing to `pyIT`

We welcome contributions! Please read the following guidelines to make the process smooth for everyone.

## Code of Conduct

This project adheres to a **[Code of Conduct](./CODE_OF_CONDUCT.md)** that expects respectful and inclusive communication. By participating, you agree to abide by its terms.

## How to Contribute

### 1. Report Issues

- Use the **GitHub Issue Tracker** to report bugs, request features, or ask questions.
- Before opening a new issue, check if it has already been reported.
- Provide a clear description, steps to reproduce, and relevant system information.

### 2. Submit Pull Requests

We encourage you to contribute code, documentation, or tests. Follow these steps:

1. **Fork** the repository.
2. **Clone** your fork and create a new branch for your feature/fix.
3. **Make your changes**, following the coding style (see below).
4. **Write or update tests** to cover your changes.
5. **Run the test suite** locally (see [TESTING.md](./docs/TESTING.md)) to ensure nothing breaks.
6. **Commit** your changes with clear, descriptive commit messages.
7. **Push** to your fork and open a pull request against the `main` branch.

## Development Environment Setup

To set up a development environment:

1. Clone the repository.
2. Create a virtual environment and install development dependencies:

   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r test-requirements.txt
   pip install -e .   # install in editable mode
   ```

3. Set the required environment variables for integration tests (if you intend to run them).

## Coding Style

- Follow **PEP 8** with a maximum line length of **100 characters**.
- Use **type hints** for all function signatures.
- Write **docstrings** for public classes and methods in the **Google style**.
- Keep functions focused and short; favor composition over inheritance where appropriate.
- Use **f‑strings** for formatting.

We recommend using a linter (e.g., `pylint`, `ruff`) and formatter (e.g., `black` or `autopep8`) to check your code before committing. However, we do not enforce a specific formatter; consistency with surrounding code is key.

## Testing

- **All new features must include tests** (unit tests, and integration tests if applicable).
- Ensure all tests pass before submitting a pull request.
- If you modify core logic, verify that existing tests still pass.

## Documentation

- Update the **README.md**, **DOCS.md**, or other documentation if your changes affect user‑visible features.
- Document new public APIs with clear docstrings.

## Pull Request Guidelines

- Keep pull requests **focused** on a single topic. Separate unrelated changes into multiple PRs.
- Provide a **clear description** of what the PR does and why.
- If the PR fixes an issue, reference it (e.g., `Fixes #123`).
- Ensure your branch is **up‑to‑date** with `main` before requesting a review.

## License

By contributing, you agree that your contributions will be licensed under the **GPL‑3.0‑or‑later** license (the same as the project).

## Questions?

Feel free to reach out via the issue tracker or discussion board. We are happy to help!

Thank you for your interest in improving `pyIT`!
