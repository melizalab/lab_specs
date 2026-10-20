import json
from pathlib import Path

import pytest

import melizalab_specs
from validation import errors

# The JSON schema files in this repo. Code blocks are validated against these
# (through melizalab_specs, which reads them from here in a source checkout) rather
# than any older versions which might be currently hosted on the live website.
spec_folder = "specs"


def get_all_json(path):
    for fname in Path(path).glob("**/*.json"):
        with open(fname) as json_file:
            try:
                yield fname, json.load(json_file)
            except json.decoder.JSONDecodeError as exc:
                raise errors.InvalidSchemaError(fname) from exc


class JsonCodeblock(pytest.Item):
    def __init__(self, *, body, extra_info, default_schema=None, **kwargs):
        super().__init__(**kwargs)
        self.body = body
        self.extra_info = extra_info
        self.default_schema = default_schema

    def runtest(self):
        body = json.loads(self.body)
        try:
            extra_keys = json.loads(self.extra_info or "{}")
        except json.decoder.JSONDecodeError as exc:
            raise errors.InvalidInfoStringError(self.extra_info) from exc
        body.update(extra_keys)
        if "$schema" not in body and self.default_schema is not None:
            body["$schema"] = self.default_schema
        validate(body)


def validate(body):
    """Validates body against the schema named in its $schema, which may refer
    to a subschema (e.g. by anchor or JSON pointer)."""
    if "$schema" not in body:
        raise errors.NoSchemaSpecifiedError()
    try:
        melizalab_specs.validate(body)
    except melizalab_specs.UnknownSchemaError as exc:
        raise errors.SchemaResolutionError(body["$schema"]) from exc
