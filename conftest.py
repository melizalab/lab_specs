import re
import pytest

from validation.jsoncodeblock import JsonCodeblock

def pytest_collect_file(parent, path):
    # collect all markdown files
    if path.ext == '.md':
        return MarkdownFile.from_parent(parent, fspath=path)

class FencedCodeblock():
    # classes that extend pytest.Node
    info_string_to_pytest_class = {
            "json": JsonCodeblock,
    }

    def __init__(self, name, info_string, body):
        """
        >>> codeblock = FencedCodeblock("test.md:3", 'json {"a": 1}', "{}")
        >>> codeblock.codeblock_class
        'json'
        >>> codeblock.extra_info
        '{"a": 1}'
        """
        self.name = name
        self.body = body
        split = info_string.split(None, maxsplit=1)
        # pad, so that we default to empty strings
        split += [''] * (2 - len(split))
        self.codeblock_class, self.extra_info = split

    def create(self, parent):
        if self.codeblock_class in self.info_string_to_pytest_class:
            return self.info_string_to_pytest_class[self.codeblock_class] \
            .from_parent(
                    parent,
                    name=self.name,
                    body=self.body,
                    extra_info=self.extra_info
            )
        raise UnsupportedCodeblockType()


class MarkdownFile(pytest.File):
    '''pytest.File representing a Markdown file, possibly containing
    codeblocks to test
    '''

    def collect(self):
        with open(self.fspath) as file_pointer:
            markdown = file_pointer.read()
        for line_num, info_string, body in MarkdownFile.extract_code_blocks(markdown):
            name = f"{self.name}:{line_num}"
            try:
                codeblock_item = FencedCodeblock(name, info_string, body)
                yield codeblock_item.create(self)
            except UnsupportedCodeblockType:
                # silently ignore unsupported codeblocks
                # (i.e. no type, or python)
                pass

    @staticmethod
    def extract_code_blocks(markdown):
        """
        Returns a generator that yields (info_string, code_block_body) tuples
        according to the CommonMark definition
        (https://spec.commonmark.org/0.29/#fenced-code-blocks)
        >>> md = '''~~~ json {pproc}
        ... code
        ... ~~~
        ... text
        ... ``` json
        ... more code
        ... ```'''
        >>> list(MarkdownFile.extract_code_blocks(md))
        [(2, 'json {pproc}', 'code\\n'), (6, 'json', 'more code\\n')]
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
            start_line_number = MarkdownFile._get_line_number(match.start('body'), markdown)
            yield (
                    start_line_number,
                    match.group('info_string').strip(),
                    match.group('body')
            )

    @staticmethod
    def _get_line_number(character_number, text):
        """
        >>> string = "12\\n23"
        >>> MarkdownFile._get_line_number(1, string)
        1
        >>> MarkdownFile._get_line_number(4, string)
        2
        """
        return text[:character_number].count('\n') + 1

class UnsupportedCodeblockType(Exception):
    pass
