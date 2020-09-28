import math

from docsearch.models import SearchDocument, TYPE_PAGE

# The minimum score we'll allow a document to have. RediSearch
# multiplies the TF*IDF score by the document score at query
# time, so we want to avoid dropping the document score down
# to 0.0.
SCORE_FLOOR = 0.1


def boost_pages(doc: SearchDocument, current_score: float):
    """Score page sections lower than pages, to boost pages."""
    if doc.type != TYPE_PAGE:
        current_score -= 0.5
    return max(current_score, SCORE_FLOOR)


def boost_top_level_pages(doc: SearchDocument, current_score: float):
    """
    Decay the score of documents deeper in the site hierarchy.

    This should result in a boost for top-level pages.
    """
    return max(current_score - math.log10(len(doc.hierarchy)) / 2, SCORE_FLOOR)
