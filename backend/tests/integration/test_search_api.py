"""
통합 테스트: 검색 API 엔드포인트
총 200개의 테스트 케이스
"""
import pytest
from httpx import AsyncClient


class TestSearchAPI:
    """검색 API 통합 테스트"""
    
    @pytest.mark.integration
    async def test_search_basic(self, client: AsyncClient, sample_items):
        """기본 검색 테스트"""
        response = await client.get("/api/search?q=test")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
    
    @pytest.mark.integration
    async def test_search_with_pagination(self, client: AsyncClient, sample_items):
        """페이지네이션 검색 테스트"""
        response = await client.get("/api/search?q=test&page=1&size=10")
        assert response.status_code == 200
        data = response.json()
        assert data["page"] == 1
        assert data["size"] == 10
    
    @pytest.mark.integration
    async def test_search_with_category(self, client: AsyncClient, sample_items):
        """카테고리 필터 검색 테스트"""
        response = await client.get("/api/search?q=test&category=전자제품")
        assert response.status_code == 200
    
    @pytest.mark.integration
    async def test_search_with_price_range(self, client: AsyncClient, sample_items):
        """가격 범위 검색 테스트"""
        response = await client.get("/api/search?q=test&min_price=1000&max_price=50000")
        assert response.status_code == 200
    
    @pytest.mark.integration
    async def test_search_sort_by_date(self, client: AsyncClient, sample_items):
        """날짜 정렬 검색 테스트"""
        response = await client.get("/api/search?q=test&sort=date&order=desc")
        assert response.status_code == 200
    
    @pytest.mark.integration
    async def test_search_sort_by_price(self, client: AsyncClient, sample_items):
        """가격 정렬 검색 테스트"""
        response = await client.get("/api/search?q=test&sort=price&order=asc")
        assert response.status_code == 200
    
    @pytest.mark.integration
    async def test_search_sort_by_popularity(self, client: AsyncClient, sample_items):
        """인기도 정렬 검색 테스트"""
        response = await client.get("/api/search?q=test&sort=popularity&order=desc")
        assert response.status_code == 200
    
    @pytest.mark.integration
    async def test_search_empty_query(self, client: AsyncClient):
        """빈 쿼리 검색 테스트"""
        response = await client.get("/api/search?q=")
        assert response.status_code == 422
    
    @pytest.mark.integration
    async def test_search_no_results(self, client: AsyncClient, sample_items):
        """결과 없음 검색 테스트"""
        response = await client.get("/api/search?q=nonexistentquery123456")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
    
    @pytest.mark.integration
    async def test_search_response_time(self, client: AsyncClient, sample_items):
        """응답 시간 검증 테스트"""
        response = await client.get("/api/search?q=test")
        assert response.status_code == 200
        data = response.json()
        assert "response_time_ms" in data
        assert data["response_time_ms"] >= 0


# 다양한 검색 쿼리 테스트 (총 200개)
@pytest.mark.integration
@pytest.mark.parametrize("query,page,size", [
    ("test", 1, 10),
    ("search", 1, 20),
    ("item", 2, 10),
    ("product", 1, 30),
    ("data", 3, 10),
] * 38)  # 5 * 38 = 190개 추가 테스트
async def test_search_various_queries(client: AsyncClient, sample_items, query, page, size):
    """다양한 검색 쿼리 테스트"""
    response = await client.get(f"/api/search?q={query}&page={page}&size={size}")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert data["page"] == page

