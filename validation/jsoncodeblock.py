import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator
from referencing import Registry, Resource
from referencing.exceptions import Unresolvable

from validation import errors

# All the jsonschema files defined in this repo, keyed by the URL at which they
# will be posted. Code blocks are validated against these rather than any older
# versions which might be currently hosted on the live website. Each schema is
# interpreted according to the dialect named in its own $schema (an
# unrecognized dialect is an error).
spec_folder = "specs"


def get_all_json(path):
    for fname in Path(path).glob("**/*.json"):
        with open(fname) as json_file:
            try:
                yield fname, json.load(json_file)
            except json.decoder.JSONDecodeError as exc:
                raise errors.InvalidSchemaError(fname) from exc


def build_registry(path=spec_folder):
    resources = []
    for fname, contents in get_all_json(Path(path)):
        try:
            resources.append((contents["$id"], Resource.from_contents(contents)))
        except KeyError as exc:
            raise errors.MissingSchemaIdError(fname) from exc
    return Registry().with_resources(resources)


registry = build_registry()


class JsonCodeblock(pytest.Item):
    def __init__(self, *, body, extra_info, **kwargs):
        super().__init__(**kwargs)
        self.body = body
        self.extra_info = extra_info

    def runtest(self):
        body = json.loads(self.body)
        try:
            extra_keys = json.loads(self.extra_info or "{}")
        except json.decoder.JSONDecodeError as exc:
            raise errors.InvalidInfoStringError(self.extra_info) from exc
        body.update(extra_keys)
        validate(body)


def validate(body, registry=registry):
    """Validates body against the schema named in its $schema, which may refer
    to a subschema (e.g. by anchor or JSON pointer). The referenced schema is
    interpreted in the dialect of the resource that contains it.

    >>> schema = {
    ...     "$schema": "https://json-schema.org/draft/2020-12/schema",
    ...     "$id": "https://example.com/base",
    ...     "type": "number",
    ...     "$defs": {"sub": {"$anchor": "sub", "type": "object"}},
    ... }
    >>> local = Registry().with_resource(schema["$id"], Resource.from_contents(schema))
    >>> validate({"$schema": "https://example.com/base#sub"}, registry=local)
    >>> validate({"$schema": "https://example.com/base#/$defs/sub"}, registry=local)
    """
    try:
        schema_uri = body["$schema"]
    except KeyError as exc:
        raise errors.NoSchemaSpecifiedError() from exc
    try:
        registry.resolver().lookup(schema_uri)
    except Unresolvable as exc:
        raise errors.SchemaResolutionError(schema_uri) from exc
    Draft202012Validator({"$ref": schema_uri}, registry=registry).validate(body)
