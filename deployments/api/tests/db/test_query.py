"""Unit tests for db query types and translators."""

import pytest
from stitch.api.db.query import DBQuery, Pagination, Ordering, pagination_to_db
from stitch.api.entities import PaginationParams


class TestPaginationToDb:
    def test_first_page_defaults(self):
        params = PaginationParams()
        result = pagination_to_db(params)
        assert result.offset == 0
        assert result.limit == 50

    def test_page_two(self):
        params = PaginationParams(page=2, page_size=10)
        result = pagination_to_db(params)
        assert result.offset == 10
        assert result.limit == 10

    def test_page_three_size_twenty(self):
        params = PaginationParams(page=3, page_size=20)
        result = pagination_to_db(params)
        assert result.offset == 40
        assert result.limit == 20


class TestDBQuery:
    def test_default_construction(self):
        q = DBQuery()
        assert q.pagination.offset == 0
        assert q.pagination.limit == 50
        assert q.ordering.sort_by is None
        assert q.ordering.sort_order == "asc"
        assert q.filters is None

    def test_with_pagination(self):
        q = DBQuery(pagination=Pagination(offset=20, limit=10))
        assert q.pagination.offset == 20
        assert q.pagination.limit == 10

    def test_frozen(self):
        q = DBQuery()
        with pytest.raises(AttributeError):
            q.pagination = Pagination(offset=99, limit=1)  # type: ignore[misc]
