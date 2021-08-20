'''Validate json in markdown files against schema'''
import re
import json
import jsonschema

def validate_file(schema_file, markdown_file):
    with open(schema_file) as file_pointer:
        schema = json.load(file_pointer)
    with open(markdown_file) as file_pointer:
        markdown = file_pointer.read()
    for schema_id, body in extract_code_blocks(markdown):
        try:
            body = json.loads(body)
        except json.decoder.JSONDecodeError as exc:
            raise ValueError(f"The following contains invalid JSON: {body}") from exc
        validate(schema, schema_id, body)

def validate(schema, schema_id, body):
    """
    >>> schema = { '$id': 'example.com/base',
    ... 'type': 'number',
    ... '$defs': {'$id': 'sub', 'type': 'null'}
    ... }
    >>> validate(schema, 'sub', None)
    """
    schema_store = {}
    resolver = jsonschema.RefResolver.from_schema(schema, store=schema_store)
    with_base_name = lambda ref: resolver._urljoin_cache(resolver.resolution_scope, ref).rstrip("/")
    resolver.store.store.update({with_base_name(k): v for k, v in schema['$defs'].items()})
    _, schema_by_id = resolver.resolve(schema_id)
    validator = jsonschema.Draft7Validator(schema_by_id, resolver=resolver)
    validator.validate(body)

def extract_code_blocks(markdown):
    """
    >>> md = '''
    ... ~~~ json {pproc}
    ... code
    ... ~~~
    ... text
    ... ~~~ json {pprox}
    ... more code
    ... ~~~'''
    >>> list(extract_code_blocks(md))
    [('pproc', 'code\\n'), ('pprox', 'more code\\n')]
    """
    codeblock_re = re.compile(r"~~~(?P<type>.*)\n(?P<body>(?:.*\n)*?)~~~", re.MULTILINE)
    for match in codeblock_re.finditer(markdown):
        yield extract_schema(match.group('type')), match.group('body')

def extract_schema(block_type):
    """
    >>> extract_schema("~~~ json {pproc}")
    'pproc'
    >>> extract_schema("~~~ json")
    Traceback (most recent call last):
        ...
    ValueError: No schema id specified. Code blocks should include an $id in \
curly braces. Like so: ~~~ json {pproc}
    """
    match = re.match(r".*{(?P<id>.*)}", block_type)
    if match is None:
        raise ValueError("No schema id specified. Code blocks should"
                " include an $id in curly braces. Like so:"
                " ~~~ json {pproc}")
    return match.group('id')

if __name__ == '__main__':
    import doctest
    doctest.testmod()

    validate_file('pprox.json', 'pprox.md')
