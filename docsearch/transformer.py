import json


def elide_text(text):
    return text if len(text) < 100 else f"{text[:100]}..."


def transform_documents(redis_client, docs):
    transformed = []

    for doc in docs:
        transformed.append({
            "title": doc.title,
            "section_title": doc.section_title,
            "hierarchy": json.loads(doc.hierarchy),
            "body": elide_text(doc.body),
            "url": doc.url
        })

    return transformed
