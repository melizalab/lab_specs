"""Checks of the schemas themselves, and that they reject malformed documents
(the markdown code blocks only show that valid documents are accepted)."""

import copy

import pytest
from jsonschema import Draft202012Validator, ValidationError
from jsonschema.validators import validator_for

from melizalab_specs import registry
from validation.jsoncodeblock import get_all_json, spec_folder, validate

PPROC = "https://meliza.org/spec:2/pprox.json#pproc"
STIMTRIAL = "https://meliza.org/spec:2/stimtrial.json#"


@pytest.mark.parametrize(
    "fname,schema", list(get_all_json(spec_folder)), ids=lambda x: str(x)[-20:]
)
def test_schema_is_valid_for_its_dialect(fname, schema):
    """Each schema has an $id, names a dialect the validator knows, and is valid
    under it."""
    assert "$id" in schema, f"{fname}: no $id, which is how the schema is found"
    cls = validator_for(schema, default=None)
    assert cls is not None, f"{fname}: unrecognized $schema {schema.get('$schema')}"
    cls.check_schema(schema)


def test_pproc_anchor_and_pointer_agree():
    """The point process can be referred to by its anchor or by JSON pointer."""
    resolver = registry().resolver()
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




ABFZIP = "https://meliza.org/spec:4/abfzip.json#"
METADATA = {
    "$schema": ABFZIP,
    "version": "1.0",
    "metadata": {
        "experimenter": "anc4kj",
        "animal": "ca7cb913-0888-4861-8b3b-a954b16f42ce",
        "cell": 5,
        "software": "Clampex 10.7.0.3",
        "processed_by": "org.meliza.melizalab-tools/abf-zip 2026.10.22",
    },
    "catalog": [
        {
            "path": "2016_05_26_0000.abf",
            "protocol": "IV_steps_500ms",
            "start": "2016-05-26T14:02:11",
            "sha1": "3c35fcd179a9616f57b73c657d8a9c418a36ae82",
        },
        {"path": "notes.txt", "sha1": "09ba327cbc0390cbfbb40e611f4693534f2d7312"},
        {"path": "comments.txt"},
    ],
}


def validate_abfzip(doc):
    """Validates doc against the abfzip schema, whatever its $schema says."""
    Draft202012Validator({"$ref": ABFZIP}, registry=registry()).validate(doc)


def changed(change):
    doc = copy.deepcopy(METADATA)
    change(doc)
    return doc


def test_valid_abfzip_metadata():
    validate(METADATA)
    validate_abfzip({"$schema": ABFZIP, "version": "1.0", "metadata": {}, "catalog": []})


def test_abfzip_accepts_newer_minor_versions_and_keys():
    """a 1.x reader can validate a file from a later minor version"""
    validate_abfzip(changed(lambda d: d.update(version="1.12", added_in_1_12={})))


@pytest.mark.parametrize(
    "change",
    [
        pytest.param(lambda d: d.pop("$schema"), id="no-schema"),
        pytest.param(lambda d: d.update({"$schema": "https://meliza.org/spec:4/abfzip-2.json#"}), id="other-schema"),
        pytest.param(lambda d: d.pop("version"), id="no-version"),
        pytest.param(lambda d: d.update(version="2.0"), id="version-2"),
        pytest.param(lambda d: d.update(version="1"), id="version-no-minor"),
        pytest.param(lambda d: d.update(version=1.0), id="version-number"),
        pytest.param(lambda d: d.pop("metadata"), id="no-metadata"),
        pytest.param(lambda d: d.update(metadata=[]), id="metadata-not-object"),
        pytest.param(lambda d: d["metadata"].update(experimenter=5), id="experimenter-not-string"),
        pytest.param(lambda d: d["metadata"].update(experimenter=""), id="experimenter-empty"),
        pytest.param(lambda d: d["metadata"].update(animal=None), id="animal-null"),
        pytest.param(lambda d: d["metadata"].update(cell=None), id="metadata-value-null"),
        pytest.param(lambda d: d.pop("catalog"), id="no-catalog"),
        pytest.param(lambda d: d.update(catalog={}), id="catalog-not-array"),
        pytest.param(lambda d: d["catalog"][0].pop("path"), id="record-no-path"),
        pytest.param(lambda d: d["catalog"][0].update(path="metadata.json"), id="record-metadata-json"),
        pytest.param(lambda d: d["catalog"][0].update(protocol=None), id="record-value-null"),
        pytest.param(lambda d: d["catalog"][0].update(start=20160526), id="record-start-not-string"),
        pytest.param(lambda d: d["catalog"][0].update(sha1="3C35FCD179A9616F57B73C657D8A9C418A36AE82"), id="sha1-uppercase"),
        pytest.param(lambda d: d["catalog"][0].update(sha1="3c35fcd1"), id="sha1-short"),
        pytest.param(lambda d: d["catalog"][0].update(sha1=None), id="sha1-null"),
        pytest.param(lambda d: d["metadata"].update(software=""), id="software-empty"),
        pytest.param(lambda d: d["metadata"].update(processed_by=["abf-zip 1.0"]), id="processed-by-list"),
        pytest.param(lambda d: d["metadata"].update(processed_by=""), id="processed-by-empty"),
    ],
)
def test_malformed_abfzip_metadata_rejected(change):
    with pytest.raises(ValidationError):
        validate_abfzip(changed(change))
