from docsearch.errors import ParseError


def skip_release_notes(doc):
    if 'Release Notes' in doc.title and not '2020' in doc.title:
        raise ParseError("Skipping outdated release notes")