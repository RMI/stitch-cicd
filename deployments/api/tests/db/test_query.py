"""
Unit tests for db query translators.

Currently a placeholder for anticipated complexity in sorting & filtering.
"""

from stitch.api.db.query import pagination_to_db
from stitch.api.entities import PaginationParams


class TestPaginationToDb:
    def test_first_page_defaults(self):
        result = pagination_to_db(PaginationParams())
        assert result.offset == 0
        assert result.limit == 50

    def test_page_to_offset(self):
        result = pagination_to_db(PaginationParams(page=2, page_size=10))
        assert result.offset == 10
        assert result.limit == 10
