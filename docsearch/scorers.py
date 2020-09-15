from docsearch.models import SearchDocument, TYPE_PAGE

# The minimum score we'll allow a document to have. RediSearch
# multiplies the TF*IDF score by the document score at query
# time, so we want to avoid dropping the document score down
# to 0.0.
SCORE_FLOOR = 0.10


def boost_sections(doc: SearchDocument, current_score: float):
    if doc.type == TYPE_PAGE:
        # Score pages lower than page sections.
        current_score -= max(current_score - 0.5, SCORE_FLOOR)
    return current_score
