# from doctest import DocTestParserExample
import doctest

from django.test import TestCase

from django_deepcopy import django_deepcopy

from .testapp.models import Comment, Forum, Post

IN_STRING = object()
IN_FENCED_EXAMPLE = object()
IN_INDENTED_EXAMPLE = object()


def parse_example(string):
    source = ''
    want = None
    for lineno, line in enumerate(string.split('\n')):
        if line.startswith('# Outputs: '):
            want = line.removeprefix('# Outputs: ')
        else:
            source += line + '\n'

    return source, want


class CodeExampleDocTest(doctest.DocTestParser):
    '''
    A processing class used to extract interactive examples from a string, and use them to create a DocTest object.

    '''

    def get_doctest(self, string, globs, name, filename, lineno):
        '''
        Extract all doctest examples from the given string, and collect them into a DocTest object.

        globs, name, filename, and lineno are attributes for the new DocTest object. See the documentation for DocTest for more information.
        '''
        print(self.get_examples(string))
        return doctest.DocTest(
            self.get_examples(string), globs, name, filename, lineno, docstring=None
        )

    def get_examples(self, string, name='<string>'):
        '''
        Extract all doctest examples from the given string, and return them as a list of Example objects. Line numbers are 0-based. The optional argument name is a name identifying this string, and is only used for error messages.
        '''
        return [
            part
            for part in self.parse(string, name)
            if isinstance(part, doctest.Example)
        ]

    def parse(self, string, name='<string>'):
        '''
        Divide the given string into examples and intervening text, and return them as a list of alternating Examples and strings. Line numbers for the Examples are 0-based. The optional argument name is a name identifying this string, and is only used for error messages.
        '''
        state = IN_STRING
        parts = []
        current_part = ''
        for lineno, line in enumerate(string.split('\n')):
            if line.startswith('```python'):
                if state == IN_STRING:
                    # Start of code block
                    parts.append(current_part)
                    state = IN_FENCED_EXAMPLE
                    current_part = ''
                else:
                    # End of code block
                    source, want = parse_example(current_part)
                    if want is None:
                        raise ValueError(
                            f'Code example (line {lineno}: {source}\n is missing an expected output'
                        )

                    parts.append(
                        doctest.Example(source, want, exc_msg=None, lineno=lineno)
                    )
                    current_part = ''

                    state = IN_STRING
            elif state == IN_STRING and line.startswith('    '):
                # Start of code block
                parts.append(current_part)
                state = IN_INDENTED_EXAMPLE
                current_part = line.removeprefix('    ') + '\n'
            elif (
                state == IN_INDENTED_EXAMPLE
                and line.strip() != ''
                and not line.startswith('    ')
            ):
                # End of code block
                source, want = parse_example(current_part)
                if want is None:
                    raise ValueError(
                        f'Code example (line {lineno}): {source}\n is missing an expected output'
                    )

                parts.append(doctest.Example(source, want, exc_msg=None, lineno=lineno))
                current_part = ''

                state = IN_STRING
            else:
                if state == IN_INDENTED_EXAMPLE:
                    current_part += line.removeprefix('    ') + '\n'
                else:
                    current_part += line + '\n'

        if state == IN_STRING:
            parts.append(current_part)
        elif state in (IN_FENCED_EXAMPLE, IN_INDENTED_EXAMPLE):
            source, want = parse_example(current_part)
            if want is None:
                raise ValueError(
                    f'Code example (line {lineno}: {source}\n is missing an expected output'
                )
            parts.append(doctest.Example(source, want, exc_msg=None, lineno=lineno))

        print(parts)
        return parts


def test_doctest():
    doctest.testfile(
        '../README.md',
        module_relative=True,
        name=None,
        package=None,
        globs=None,
        verbose=None,
        report=True,
        optionflags=0,
        extraglobs=None,
        raise_on_error=False,
        parser=CodeExampleDocTest(),
        encoding=None,
    )
