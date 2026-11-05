# Installation

## Stable release

Install the latest stable release from PyPI:

```bash
python -m pip install compas_session
```

COMPAS Session requires Python 3.12 or newer, COMPAS 3, and Pydantic 2.

## Development setup

Clone the repository and create the locked development environment with uv:

```bash
git clone https://github.com/blockresearchgroup/compas_session.git
cd compas_session
uv sync --frozen --group dev --group docs
```

Run the same checks used by continuous integration:

```bash
uv run ruff check .
uv run ruff format --check .
uv run pyright
uv run pytest
uv run mkdocs build --strict
```

Thin Invoke aliases remain available, for example `uv run invoke test` and
`uv run invoke docs`. The direct commands above are authoritative.
