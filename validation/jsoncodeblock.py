import json
from pathlib import Path
import re
from urllib.parse import urljoin

import pytest
import jsonschema

CurrentValidator = jsonschema.Draft7Validator

# set up hardcoded global variable that will store all the jsonschema
# files defined in this repo, keyed by the URL at which they will be
# posted. This dictionary will be used by a jsonschema.RefResolver to
# ensure that tests are verified against the schemas in this repo
# rather than any older versions which might be currently hosted on
# the live website.
spec_folder = 'specs'
def get_all_json(path):
    for fname in Path(path).glob('**/*.json'):
        with open(fname) as json_file:
            yield json.load(json_file)

def build_url_store():
    for contents in get_all_json(Path(spec_folder)):
        yield contents['$id'], contents

prepopulated_cache = dict(build_url_store())

class JsonCodeblock(pytest.Item):
    def __init__(self, name, parent, body, extra_info):
        super().__init__(name, parent)
        self.body = body
        self.extra_info = extra_info

    def runtest(self):
        body = json.loads(self.body)
        try:
            extra_keys = json.loads(self.extra_info or '{}')
        except json.decoder.JSONDecodeError as exc:
            raise InvalidInfoStringError(self.extra_info) from exc
        body.update(extra_keys)
        self._validate(body)

    @staticmethod
    def _validate(body, store=prepopulated_cache):
        """
        >>> schema = { '$id': 'https://example.com/base',
        ... 'type': 'number',
        ... '$defs': {'sub': {'$id': '/sub', 'type': 'object'}}
        ... }
        >>> obj = {'$schema': 'https://example.com/base#/$defs/sub'}
        >>> JsonCodeblock._validate(obj, store={schema['$id']: schema})
        """
        resolver = jsonschema.RefResolver(
                base_uri='https://example.com/json',
                referrer=body,
                store=store,
        )
        try:
            schema_uri = body['$schema']
        except KeyError as exc:
            raise NoSchemaSpecifiedError() from exc
        try:
            _, schema = resolver.resolve(schema_uri)
        except jsonschema.RefResolutionError as exc:
            raise SchemaResolutionError(schema_uri) from exc
        CurrentValidator.check_schema(schema)
        validator = CurrentValidator(schema, resolver=resolver)
        validator.validate(body)

class JsonCodeblockError(Exception):
    pass

class SchemaResolutionError(JsonCodeblockError):
    def __init__(self, schema):
        self.schema = schema

    def __str__(self):
        return self.schema

class NoSchemaSpecifiedError(JsonCodeblockError):
    def __str__(self):
        return (
            'Any codeblock that is labelled as "json" must specify a'
            ' a schema. Schemas can be specified with the "$schema"'
            ' key in the body of the codeblock or as a key in an'
            ' object after "json" in the info string (which will be'
            ' merged with the object in the body), like so:\n'
            '``` json {"$schema": "https://example.com/schema"}\n'
            '{}\n```'
        )

class InvalidInfoStringError(JsonCodeblockError):
    def __init__(self, info_string):
        self.info_string = info_string

    def __str__(self):
        return (
            "Could not parse the following info string object as"
            f" valid JSON: '{self.info_string}'"
        )
