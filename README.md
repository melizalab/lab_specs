# Meliza Lab Specifications

## Validating jsonschema

The JSON schemas in `specs/` and the JSON examples in the markdown documents
(fenced code blocks marked `json`) are validated with pytest. With
[uv](https://docs.astral.sh/uv/):

```
uv run pytest
```

Each example is validated against the schema named in its `$schema` key. For
examples that don't have one, set a default with an `example_schema` key in
the document's YAML front matter:

```
---
title: pprox specification
example_schema: https://meliza.org/spec:2/pprox.json#pproc
---
```

(A schema can also be given in the code block's info string, as in
`~~~ json {"$schema": "..."}`, but kramdown, which compiles these documents
for the website, doesn't accept that.)

uv installs the dependencies listed in `pyproject.toml`, at the versions
recorded in `uv.lock`, into a local `.venv`. To update them, run
`uv lock --upgrade`.
