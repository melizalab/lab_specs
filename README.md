# Meliza Lab Specifications

## Validating jsonschema

The JSON schemas in `specs/` and the JSON examples in the markdown documents
(fenced code blocks marked `json`) are validated with pytest. With
[uv](https://docs.astral.sh/uv/):

```
uv run pytest
```

uv installs the dependencies listed in `pyproject.toml`, at the versions
recorded in `uv.lock`, into a local `.venv`. To update them, run
`uv lock --upgrade`.
