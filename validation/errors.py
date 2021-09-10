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


class InvalidSchemaError(JsonCodeblockError):
    def __init__(self, fname):
        self.fname = fname

    def __str__(self):
        return (
            f"Failed to decode the JSON file {self.fname}"
        )


class MissingSchemaIdError(JsonCodeblockError):
    def __init__(self, fname):
        self.fname = fname

    def __str__(self):
        return (
            f"Could not find the $id key in {self.fname},"
            " which is needed to prepopulate the jsonschema"
            " reference resolution cache so that references"
            " are resolved to local versions"
        )
