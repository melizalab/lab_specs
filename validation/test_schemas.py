"""Checks of the schemas themselves, and that they reject malformed documents
(the markdown code blocks only show that valid documents are accepted)."""

import copy

import pytest
from jsonschema import ValidationError
from jsonschema.validators import validator_for

from validation.jsoncodeblock import get_all_json, registry, spec_folder, validate

PPROC = "https://meliza.org/spec:2/pprox.json#pproc"
STIMTRIAL = "https://meliza.org/spec:2/stimtrial.json#"


@pytest.mark.parametrize(
    "fname,schema", list(get_all_json(spec_folder)), ids=lambda x: str(x)[-20:]
)
def test_schema_is_valid_for_its_dialect(fname, schema):
    """Each schema names a dialect the validator knows, and is valid under it."""
    cls = validator_for(schema, default=None)
    assert cls is not None, f"{fname}: unrecognized $schema {schema.get('$schema')}"
    cls.check_schema(schema)


def test_pproc_anchor_and_pointer_agree():
    """The point process can be referred to by its anchor or by JSON pointer."""
    resolver = registry.resolver()
    anchor = resolver.lookup(PPROC).contents
    pointer = resolver.lookup("https://meliza.org/spec:2/pprox.json#/$defs/pproc").contents
    assert anchor is pointer


TRIAL = {
    "offset": 13.4878,
    "index": 4,
    "interval": [-0.5, 2.2423],
    "stimulus": {"name": "arc605_G", "interval": [0.0, 1.2]},
    "aux": [{"name": "led", "interval": [0.0, 1.0]}],
    "events": [0.051, 0.712],
}
COLLECTION = {"$schema": STIMTRIAL, "aux_tracks": {"led": {"channel": "ADC4"}}, "pprox": [TRIAL]}


def broken(change):
    doc = copy.deepcopy(COLLECTION)
    change(doc)
    return doc


def test_valid_collection():
    validate(COLLECTION)


@pytest.mark.parametrize(
    "change",
    [
        pytest.param(lambda d: d["pprox"][0].pop("events"), id="no-events"),
        pytest.param(lambda d: d["pprox"][0].pop("interval"), id="no-interval"),
        pytest.param(lambda d: d["pprox"][0].__setitem__("interval", [0, 1, 2]), id="interval-3"),
        pytest.param(lambda d: d["pprox"][0].pop("stimulus"), id="no-stimulus"),
        pytest.param(
            lambda d: d["pprox"][0]["stimulus"].__setitem__("interval", [0.0]),
            id="stimulus-interval-1",
        ),
        pytest.param(lambda d: d["pprox"][0]["aux"][0].pop("name"), id="aux-no-name"),
        pytest.param(
            lambda d: d["pprox"][0]["aux"][0].__setitem__("interval", [0.0, "1"]),
            id="aux-interval-not-number",
        ),
        pytest.param(lambda d: d["pprox"][0].__setitem__("aux", {"led": [0, 1]}), id="aux-not-array"),
        pytest.param(lambda d: d.__setitem__("aux_tracks", {"led": "ADC4"}), id="aux-tracks-not-object"),
    ],
)
def test_malformed_collections_rejected(change):
    with pytest.raises(ValidationError):
        validate(broken(change))


def test_pproc_interval_optional():
    """pprox 1.0 does not require a point process to have an interval."""
    validate({"$schema": PPROC, "events": [0.1, 0.2]})


def test_stimtrial_requires_interval():
    """stimtrial requires each trial to have an interval."""
    with pytest.raises(ValidationError, match="'interval' is a required property"):
        validate(broken(lambda d: d["pprox"][0].pop("interval")))
