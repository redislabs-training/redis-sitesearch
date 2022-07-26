from sitesearch.models import SearchDocument, TYPE_PAGE
from sitesearch.sites.command_processor import *
from os import path

COMMANDS_LANDING_PAGE = SearchDocument(
    doc_id="redisio://commands",  # Note: this is a fake document ID,
    title="Redis Commands",
    section_title="",
    hierarchy=["Redis"],
    s="commands",
    url="/commands/",
    body="Documentation for all Redis commands",
    type=TYPE_PAGE,
    position=0
)

COMMUNITY_LANDING_PAGE = SearchDocument(
    doc_id="redisio://community",  # Note: this is a fake document ID,
    title="Redis Community",
    section_title="",
    hierarchy=["Redis"],
    s="community",
    url="/community/",
    body="Redis community, code of conduct, mailing list, news, etc.",
    type=TYPE_PAGE,
    position=0
)

DOWNLOAD_LANDING_PAGE = SearchDocument(
    doc_id="redisio://download",  # Note: this is a fake document ID,
    title="Redis Downloads",
    section_title="",
    hierarchy=["Redis"],
    s="download",
    url="/download/",
    body="Download Redis and Redis Stack",
    type=TYPE_PAGE,
    position=0
)

STACK_LANDING_PAGE = SearchDocument(
    doc_id="redisio://docs/stack",  # Note: this is a fake document ID,
    title="Redis Stack",
    section_title="",
    hierarchy=["Redis"],
    s="docs",
    url="/docs/stack/",
    body="Introduction to Redis Stack",
    type=TYPE_PAGE,
    position=0
)

REDIS_IO_LANDING_PAGES = {
    'com': COMMANDS_LANDING_PAGE,
    'comm': COMMANDS_LANDING_PAGE,
    'comma': COMMANDS_LANDING_PAGE,
    'comman': COMMANDS_LANDING_PAGE,
    'command': COMMANDS_LANDING_PAGE,
    'commands': COMMANDS_LANDING_PAGE,

    'commu': COMMUNITY_LANDING_PAGE,
    'commun': COMMUNITY_LANDING_PAGE,
    'communi': COMMUNITY_LANDING_PAGE,
    'communit': COMMUNITY_LANDING_PAGE,
    'community': COMMUNITY_LANDING_PAGE,

    'down': DOWNLOAD_LANDING_PAGE,
    'download': DOWNLOAD_LANDING_PAGE,
    'downloads': DOWNLOAD_LANDING_PAGE,

    'stac': STACK_LANDING_PAGE,
    'stack': STACK_LANDING_PAGE,
}

commands_filename = path.join(path.dirname(__file__), 'commands.json')
command_pages = process_commands(commands_filename)

REDIS_IO_LANDING_PAGES.update(command_pages)