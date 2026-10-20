"""The JSON schemas of the Meliza lab's data specifications.

The schemas are those published at https://meliza.org/spec:N/..., keyed by their
`$id`. `schemas()` and `schema()` need nothing beyond the standard library;
`registry()` and `validate()` need the `validate` extra (jsonschema).
"""

import json
from functools import cache
from importlib.resources import files
from importlib.resources.abc import Traversable
from pathlib import Path
from typing import Any

__all__ = ["UnknownSchemaError", "registry", "schema", "schemas", "validate"]


class UnknownSchemaError(LookupError):
    """A document names a schema that isn't one of these specifications."""


def _spec_folder() -> Traversable:
    # an installed package has the specs copied into it; a source checkout reads
    # them from the repository's specs/ folder, which is what's published
    installed = files(__name__) / "specs"
    if installed.is_dir():
        return installed
    return Path(__file__).parent.parent / "specs"


@cache
def schemas() -> dict[str, dict[str, Any]]:
    """Returns every schema, keyed by its `$id`."""
    out = {}
    for path in _spec_folder().iterdir():
        if path.name.endswith(".json"):
            contents = json.loads(path.read_text())
            out[contents["$id"]] = contents
    return out


def schema(uri: str) -> dict[str, Any]:
    """Returns the schema with `$id` uri. A trailing `#` is optional."""
    found = schemas()
    for candidate in (uri, uri.rstrip("#"), uri.rstrip("#") + "#"):
        if candidate in found:
            return found[candidate]
    raise UnknownSchemaError(uri)


def _need_validate_extra(err: ImportError):
    raise ImportError(
        f"{err.name} is needed to validate; install melizalab-specs[validate]"
    ) from err


def registry():
    """Returns a `referencing.Registry` of the schemas, for resolving references
    between them (e.g. stimtrial's to pprox) and subschemas by anchor."""
    try:
        from referencing import Registry, Resource
    except ImportError as err:
        _need_validate_extra(err)

    return Registry().with_resources(
        (uri, Resource.from_contents(contents))
        for uri, contents in schemas().items()
    )


def validate(document: Any, schema_uri: str | None = None) -> None:
    """Validates document against the schema named in its `$schema` key, or
    schema_uri if given. The URI may refer to a subschema, e.g.
    `https://meliza.org/spec:2/pprox.json#pproc`.

    Raises jsonschema.ValidationError if the document doesn't follow the schema,
    UnknownSchemaError if the schema isn't one of these specifications, and
    ValueError if no schema is named.
    """
    try:
        from jsonschema import Draft202012Validator
        from referencing.exceptions import Unresolvable
    except ImportError as err:
        _need_validate_extra(err)

    if schema_uri is None:
        try:
            schema_uri = document["$schema"]
        except (KeyError, TypeError) as err:
            raise ValueError("the document has no $schema") from err
    reg = registry()
    try:
        reg.resolver().lookup(schema_uri)
    except Unresolvable as err:
        raise UnknownSchemaError(schema_uri) from err
    Draft202012Validator({"$ref": schema_uri}, registry=reg).validate(document)
