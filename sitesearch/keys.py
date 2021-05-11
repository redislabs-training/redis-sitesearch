

class Keys:
    def __init__(self, prefix: str):
        self.prefix = prefix

    async def document(self, url: str, doc_id: str) -> str:
        """The key used for a single document in the index.

        This key ends with an ID because each URL might have several
        documents in the index, one for the page as a whole and one
        per H2 we scraped (if there were H2 elements on the page).
        """
        return f"{self.prefix}:{url}:doc:{doc_id}"

    async def last_index(self, url: str) -> str:
        """The last time we indexed a URL."""
        return f"{self.prefix}:{url}:last_indexing_time"

    async def index_alias(self, url: str) -> str:
        """The index alias we use for a URL."""
        return f"{self.prefix}:{url}"

    async def index_lock(self, url: str) -> str:
        """A simple lock taken while indexing."""
        return f"{self.prefix}:{url}:lock"

    async def index_prefix(self, url: str) -> str:
        """The prefix we use for a RediSearch index.

        This becomes part of the index definition and controls which
        documents (Hashes) RediSearch will index.
        """
        return f"{self.prefix}:{url}"

    async def startup_indexing_job_ids(self) -> str:
        """A Set containing the startup indexing task IDs.

        We clear this out as the tasks finish.
        """
        return f"{self.prefix}:startup_indexing_tasks"

    async def site_urls_current(self, index_alias: str) -> str:
        """All the URLs currently indexed for a site."""
        return f"{self.prefix}:{index_alias}:{{urls}}:current"

    async def site_urls_new(self, index_alias: str) -> str:
        """All the URLs newly indexed by an indexing task for a site.

        We use this and site_urls_current() to clean up old URLs that we
        indexed from a site in the past but that are no longer on the site.
        """
        return f"{self.prefix}:{index_alias}:{{urls}}:new"
