from docsearch.errors import ParseError


def skip_release_notes(doc):
    if 'Release Notes' in doc.title:
        raise ParseError("Skipping release notes")