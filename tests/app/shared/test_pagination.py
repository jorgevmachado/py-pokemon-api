from unittest.mock import patch

import pytest
from pydantic import ValidationError

from app.shared.pagination import exception_pagination, is_paginate, limit_paginate
from app.shared.schemas import FilterPage


class TestPaginationLimitPaginate:
    @staticmethod
    def test_limit_paginate_no_limit():
        limit = 100
        result = limit_paginate()
        assert result == limit

    @staticmethod
    def test_limit_paginate_with_limit():
        limit = 50
        result = limit_paginate(limit=limit)
        assert result == limit

    @staticmethod
    def test_limit_paginate_with_limit_and_max_limit():
        max_limit = 50
        limit = 60

        result = limit_paginate(limit=limit, max_limit=max_limit)
        assert result == max_limit


class TestPaginationIsPaginate:
    @staticmethod
    def test_is_paginate_no_page_filter():
        result = is_paginate()
        assert not result

    @staticmethod
    def test_is_paginate_with_page_filter():
        result = is_paginate(FilterPage(offset=1, limit=10))
        assert result


class TestPaginationExceptionPagination:
    @staticmethod
    def test_exception_pagination_not_paginate():
        """Should return empty list when no pagination params are provided"""
        result = exception_pagination()
        assert result == []
        assert isinstance(result, list)

    @staticmethod
    def test_exception_pagination_paginate_valid():
        """Should return paginated page when FilterPage is valid"""
        result = exception_pagination(FilterPage(offset=0, limit=10))
        assert hasattr(result, 'items')
        assert len(result.items) == 0
        assert result.total == 0

    @staticmethod
    def test_exception_pagination_with_exception_invalid_offset():
        """Should raise ValidationError when offset is negative"""
        with pytest.raises(ValidationError):
            FilterPage(offset=-1, limit=10)

    @staticmethod
    def test_exception_pagination_with_exception_invalid_limit():
        """Should raise ValidationError when limit is zero"""
        with pytest.raises(ValidationError):
            FilterPage(offset=0, limit=0)

    @staticmethod
    def test_exception_pagination_with_high_offset():
        """Should return paginated page with high offset value"""
        limit = 10
        offset = 1000
        result = exception_pagination(FilterPage(offset=offset, limit=limit))

        assert hasattr(result, 'items')
        assert isinstance(result.items, list)
        assert len(result.items) == 0
        assert result.total == 0
        assert result.offset == offset
        assert result.limit == limit

    @staticmethod
    def test_exception_pagination_with_max_limit():
        """Should return paginated page with maximum limit value"""
        limit = 100
        result = exception_pagination(FilterPage(offset=0, limit=limit))

        assert hasattr(result, 'items')
        assert len(result.items) == 0
        assert result.total == 0
        assert result.limit == limit

    @staticmethod
    def test_exception_pagination_only_offset_no_limit():
        """Should return empty list when only offset is provided"""
        result = exception_pagination(FilterPage(offset=10, limit=None))

        assert result == []
        assert isinstance(result, list)

    @staticmethod
    def test_exception_pagination_only_limit_no_offset():
        """Should return empty list when only limit is provided"""
        result = exception_pagination(FilterPage(offset=None, limit=10))

        assert result == []
        assert isinstance(result, list)

    @staticmethod
    def test_exception_pagination_catch_exception():
        """Should catch exception and return empty list when LimitOffsetParams raises error"""
        with patch('app.shared.pagination.is_paginate', side_effect=Exception('Test error')):
            result = exception_pagination(FilterPage(offset=0, limit=10))

            # Should return empty list due to exception handling
            assert result == []
            assert isinstance(result, list)

    @staticmethod
    def test_exception_pagination_catch_exception_limit_offset_params():
        """Should catch exception when LimitOffsetParams creation fails"""
        # Mock is_paginate to return True so we enter the try block
        # Then mock LimitOffsetParams to raise an exception
        with (
            patch('app.shared.pagination.is_paginate', return_value=True),
            patch(
                'app.shared.pagination.LimitOffsetParams',
                side_effect=ValueError('Invalid params'),
            ),
        ):
            result = exception_pagination(FilterPage(offset=0, limit=10))

            # Should return empty list due to exception handling
            assert result == []
            assert isinstance(result, list)
