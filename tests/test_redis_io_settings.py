import pytest

from sitesearch.sites.redis_io_landing_pages import REDIS_IO_LANDING_PAGES

def test_get_landing_page():
   assert REDIS_IO_LANDING_PAGES['get'].url == '/commands/get/'
   assert REDIS_IO_LANDING_PAGES['get'].doc_id == 'redisio://commands/landing/get'
   assert REDIS_IO_LANDING_PAGES['get'].body == 'Get the value of a key'

def test_correct_number_of_landing_pages():
   assert len(REDIS_IO_LANDING_PAGES.keys()) == 723

def test_ignore_commands_with_spaces():
   assert 'acl' in REDIS_IO_LANDING_PAGES
   assert 'acl list' not in REDIS_IO_LANDING_PAGES