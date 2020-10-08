from sitesearch.models import SearchDocument, TYPE_PAGE


CLOUD_LANDING_PAGE = SearchDocument(
    doc_id="redislabs://docs/landing/cloud",  # Note: this is a fake document ID,
    title="Redis Enterprise Cloud",
    section_title="",
    hierarchy=["Redis Enterprise Cloud"],
    url="latest/rc/",
    body="Redis Enterprise <b>Cloud</b> delivers a cost-effective, fully "
            "managed Database-as-a-Service (DBaaS) offering, fully hosted on public clouds.",
    type=TYPE_PAGE,
    position=0
)

SOFTWARE_LANDING_PAGE = SearchDocument(
    doc_id="redislabs://docs/landing/software",  # Note: this is a fake document ID,
    title="Redis Enterprise Software",
    section_title="",
    hierarchy=["Redis Enterprise Software"],
    url="latest/rs/",
    body="Redis Enterprise is a robust, in-memory database platform built by the same people "
         "who develop open-source Redis.",
    type=TYPE_PAGE,
    position=0
)

ACTIVE_ACTIVE_LANDING_PAGE = SearchDocument(
    doc_id="redislabs://docs/landing/active-active",  # Note: this is a fake document ID,
    title="Geo-Distributed <b>Active</b>-Active Redis Applications",
    section_title="",
    hierarchy=["Redis Enterprise Software", "Concepts and Architecture", "Geo-Distributed Active-Active Redis Applications"],
    url="latest//",
    body="Developing globally distributed applications can be challenging, as developers "
         "have to think about race conditions and complex combinations of events under "
         "geo-failovers and cross-region write conflicts.",
    type=TYPE_PAGE,
    position=0
)


LANDING_PAGES = {
    'cloud': CLOUD_LANDING_PAGE,
    'redis cloud': CLOUD_LANDING_PAGE,
    'redis enterprise cloud': CLOUD_LANDING_PAGE,
    'rc': CLOUD_LANDING_PAGE,

    'software': SOFTWARE_LANDING_PAGE,
    'rs': SOFTWARE_LANDING_PAGE,

    'active': ACTIVE_ACTIVE_LANDING_PAGE,
    'active-active': ACTIVE_ACTIVE_LANDING_PAGE,
}
