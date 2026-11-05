# Contributing

Contributions are welcome and very much appreciated!

## Code contributions

We accept code contributions through pull requests.
In short, this is how that works.

1. Fork [the repository](https://github.com/blockresearchgroup/compas_session) and clone the fork.
2. Install the locked development and documentation environments:

   ```bash
   uv sync --frozen --group dev --group docs
   ```

3. Make sure all tests pass:

   ```bash
   uv run pytest
   ```

4. Create a branch for your changes.
5. Make sure all tests still pass:

   ```bash
   uv run ruff check .
   uv run ruff format --check .
   uv run pyright
   uv run pytest
   uv run mkdocs build --strict
   ```

6. Commit your changes and push your branch to GitHub.
7. Create a [pull request](https://help.github.com/articles/about-pull-requests/) through the GitHub website.

The direct uv commands above are authoritative. Thin Invoke aliases are also
available for convenience:

* `uv run invoke check`: Run lint, formatting, and typing checks.
* `uv run invoke docs`: Build documentation in strict mode.
* `uv run invoke test`: Run the test suite.
* `uv run invoke --list`: Show available tasks.

## Bug reports

When [reporting a bug](https://github.com/blockresearchgroup/compas_session/issues) please include:

* Operating system name and version.
* Any details about your local setup that might be helpful in troubleshooting.
* Detailed steps to reproduce the bug.

## Feature requests

When [proposing a new feature](https://github.com/blockresearchgroup/compas_session/issues) please include:

* Explain in detail how it would work.
* Keep the scope as narrow as possible, to make it easier to implement.
