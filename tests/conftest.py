import urllib
import urllib.parse

import pytest

from rfp_scraper import db


@pytest.fixture(scope="session", autouse=True)
def assert_database_is_local():
    database_url = urllib.parse.urlparse(db.get_database_url())
    assert database_url.hostname == "postgres", "Database must be local"
