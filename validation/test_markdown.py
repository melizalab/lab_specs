'''Validate json in markdown files against schema'''
import re
import json
from urllib.parse import urljoin
import jsonschema

def validate_file(schema_file, markdown_file):
    with open(schema_file) as file_pointer:
        schema = json.load(file_pointer)
    with open(markdown_file) as file_pointer:
        markdown = file_pointer.read()
    for info_string, body in extract_code_blocks(markdown):
        try:
            schema_id = extract_schema(info_string)
        except ValueError as exc:
            raise ValueError((f"Could not determine schema for block: {body}")) from exc
        validate(schema, schema_id, load_json(body))

def validate(base_schema, schema_id, body):
    """
    >>> schema = { '$id': 'example.com/base',
    ... 'type': 'number',
    ... '$defs': {'$id': 'sub', 'type': 'null'}
    ... }
    >>> validate(schema, 'sub', None)
    """
    resolver = jsonschema.RefResolver.from_schema(base_schema)
    with_base_name = lambda ref: urljoin(resolver.resolution_scope, ref)
    resolver.store.store.update(
            {with_base_name(k): v for k, v in base_schema['$defs'].items()}
    )
    _, schema_from_id = resolver.resolve(schema_id)
    validator = jsonschema.Draft7Validator(schema_from_id, resolver=resolver)
    validator.validate(body)

def extract_code_blocks(markdown):
    """
    Returns a generator that yields (info_string, code_block_body) tuples
    according to the CommonMark definition
    (https://spec.commonmark.org/0.29/#fenced-code-blocks)
    >>> md = '''
    ... ~~~ json {pproc}
    ... code
    ... ~~~
    ... text
    ... ``` json
    ... more code
    ... ```'''
    >>> list(extract_code_blocks(md))
    [('json {pproc}', 'code\\n'), ('json', 'more code\\n')]
    """
    codeblock_re = re.compile(
            (
                r"^ {0,3}(?P<fence>```+|~~~+)(?P<info_string>[^~`\n]*)\n"
                r"(?P<body>[\s\S]*?)"
                r"^ {0,3}(?P=fence)"
            ),
            re.MULTILINE
    )
    for match in codeblock_re.finditer(markdown):
        yield match.group('info_string').strip(), match.group('body')

def extract_schema(info_string):
    """
    >>> extract_schema("json {pproc}")
    'pproc'
    >>> extract_schema("json")
    Traceback (most recent call last):
        ...
    ValueError: Could not parse schema ID from info string 'json'. \
Code blocks should include an $id in curly braces. Like so: ~~~ json {pproc}

    """
    match = re.match(r".*{(?P<id>.*)}", info_string)
    if match is None:
        raise ValueError(f"Could not parse schema ID from info string '{info_string}'."
                " Code blocks should include an $id in curly braces. Like so:"
                " ~~~ json {pproc}")
    return match.group('id')

def load_json(text):
    """Load JSON with more clear error message"""
    try:
        return json.loads(text)
    except json.decoder.JSONDecodeError as exc:
        raise ValueError(f"The following contains invalid JSON: {text}") from exc

def test_pprox():
    validate_file('specs/pprox.json', 'specs/pprox.md')
