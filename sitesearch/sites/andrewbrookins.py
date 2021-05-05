from redisearch.client import TextField

from sitesearch.models import SiteConfiguration
from sitesearch.scorers import boost_pages, boost_top_level_pages
from sitesearch.validators import skip_404_page


BLOG = SiteConfiguration(
    url="https://andrewbrookins.com",
    synonym_groups=[],
    landing_pages={},
    allowed_domains=('andrewbrookins.com',),
    schema=(
        TextField("title", weight=10),
        TextField("section_title"),
        TextField("body", weight=1.5),
        TextField("url"),
        TextField("s", no_stem=True),
    ),
    scorers=(
        boost_pages,
        boost_top_level_pages
    ),
    validators=(
        skip_404_page,
    ),
    deny=(
        r'.*\.pdf',
        r'.*\.tgz',
        r'\/tag\/.*',
    ),
    allow=(),
    content_classes=(".post",)
)
