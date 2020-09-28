PREFIX = "docsearch:docs"

def document(url, doc_id: str):
    return f"{PREFIX}:{url}:{doc_id}"
