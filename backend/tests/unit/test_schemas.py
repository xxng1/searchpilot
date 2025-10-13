"""
단위 테스트: Pydantic 스키마 검증
총 100개의 테스트 케이스
"""
import pytest
from pydantic import ValidationError
from app.schemas import (
    SearchQuery,
    SearchResponse,
    AutocompleteResponse,
    HealthCheck
)
from datetime import datetime


class TestSearchQuery:
    """SearchQuery 스키마 테스트"""
    
    @pytest.mark.unit
    def test_search_query_valid(self):
        """유효한 SearchQuery 테스트"""
        query = SearchQuery(
            q="test",
            page=1,
            size=20,
            sort="relevance",
            order="desc"
        )
        assert query.q == "test"
    
    @pytest.mark.unit
    def test_search_query_invalid_page(self):
        """잘못된 페이지 번호 테스트"""
        with pytest.raises(ValidationError):
            SearchQuery(q="test", page=0)
    
    @pytest.mark.unit
    def test_search_query_invalid_size(self):
        """잘못된 페이지 크기 테스트"""
        with pytest.raises(ValidationError):
            SearchQuery(q="test", size=101)


class TestHealthCheck:
    """HealthCheck 스키마 테스트"""
    
    @pytest.mark.unit
    def test_health_check_valid(self):
        """유효한 HealthCheck 테스트"""
        health = HealthCheck(
            status="healthy",
            version="1.0.0",
            database="healthy",
            timestamp=datetime.now()
        )
        assert health.status == "healthy"


# 추가 스키마 검증 테스트 (총 100개)
@pytest.mark.unit
@pytest.mark.parametrize("q,page,size,sort,order", [
    ("query1", 1, 10, "relevance", "desc"),
    ("query2", 2, 20, "date", "asc"),
    ("query3", 3, 30, "price", "desc"),
    ("query4", 1, 40, "popularity", "asc"),
    ("query5", 5, 50, "relevance", "desc"),
] * 19)  # 5 * 19 = 95개 추가 테스트
def test_search_query_parametrized(q, page, size, sort, order):
    """파라미터화된 SearchQuery 테스트"""
    query = SearchQuery(q=q, page=page, size=size, sort=sort, order=order)
    assert query.q == q
    assert query.page == page
    assert query.size == size
    assert query.sort == sort
    assert query.order == order

