# Meliza Lab Specifications

The specifications for the Meliza lab's data formats, published at
<https://meliza.org/specifications/>. Each is a markdown document in `specs/`,
with a JSON schema for formats that are JSON.

## Python package

The schemas are also a Python package, `melizalab-specs`, so programs that read
or write these formats can validate against them without fetching them from the
website or keeping their own copies:

```
pip install "melizalab-specs[validate]"
```

```python
import melizalab_specs

melizalab_specs.schemas()           # every schema, keyed by its $id
melizalab_specs.schema("https://meliza.org/spec:2/pprox.json")
melizalab_specs.validate(document)  # against the schema named in its $schema
melizalab_specs.validate(trial, "https://meliza.org/spec:2/pprox.json#pproc")
```

`validate` raises `jsonschema.ValidationError` for a document that doesn't
follow its schema, and `melizalab_specs.UnknownSchemaError` for a schema that
isn't one of these. Reading the schemas needs no dependencies; validating needs
the `validate` extra (jsonschema).

A new release of the package carries changes to the schemas to the programs
that use them. Releases are published to PyPI from version tags.

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
recorded in `uv.lock`, into a local `.venv`, along with the package itself.
To update them, run `uv lock --upgrade`.
