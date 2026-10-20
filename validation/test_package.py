"""The melizalab_specs package: finding and validating against the schemas."""

import json
from pathlib import Path

import pytest
from jsonschema import ValidationError

import melizalab_specs

PPROX = "https://meliza.org/spec:2/pprox.json"
STIMTRIAL = "https://meliza.org/spec:2/stimtrial.json#"


def test_every_schema_file_is_found():
    ids = {json.loads(p.read_text())["$id"] for p in Path("specs").glob("*.json")}
    assert set(melizalab_specs.schemas()) == ids


@pytest.mark.parametrize("uri", [PPROX, PPROX + "#", STIMTRIAL, STIMTRIAL.rstrip("#")])
def test_schema_is_found_with_or_without_trailing_hash(uri):
    assert melizalab_specs.schema(uri)["$id"].rstrip("#") == uri.rstrip("#")


def test_unknown_schema():
    with pytest.raises(melizalab_specs.UnknownSchemaError):
        melizalab_specs.schema("https://meliza.org/spec:9/nothing.json")
    with pytest.raises(melizalab_specs.UnknownSchemaError):
        melizalab_specs.validate({"$schema": "https://meliza.org/spec:9/nothing.json"})


@pytest.mark.parametrize("ref", ["#pproc", "#/$defs/pproc"])
def test_validate_subschema_by_anchor_or_pointer(ref):
    melizalab_specs.validate({"$schema": PPROX + ref, "events": [0.1]})
    with pytest.raises(ValidationError):
        melizalab_specs.validate({"$schema": PPROX + ref, "events": "0.1"})


def test_validate_follows_references_between_schemas():
    # stimtrial refers to pprox for the point process
    trial = {"events": "not a list", "interval": [0, 1], "stimulus": {"name": "s", "interval": [0, 1]}}
    with pytest.raises(ValidationError):
        melizalab_specs.validate({"$schema": STIMTRIAL, "pprox": [trial]})


def test_validate_with_a_given_schema():
    melizalab_specs.validate({"events": [0.1]}, PPROX + "#pproc")


def test_validate_needs_a_schema():
    with pytest.raises(ValueError, match="no \\$schema"):
        melizalab_specs.validate({"events": [0.1]})
