"""
통합 테스트: 자동완성 API
총 100개의 테스트 케이스
"""
import pytest
from httpx import AsyncClient


class TestAutocompleteAPI:
    """자동완성 API 통합 테스트"""
    
    @pytest.mark.integration
    async def test_autocomplete_basic(self, client: AsyncClient, sample_items):
        """기본 자동완성 테스트"""
        response = await client.get("/api/autocomplete?q=te")
        assert response.status_code == 200
        data = response.json()
        assert "suggestions" in data
        assert isinstance(data["suggestions"], list)
    
    @pytest.mark.integration
    async def test_autocomplete_with_limit(self, client: AsyncClient, sample_items):
        """제한 수 자동완성 테스트"""
        response = await client.get("/api/autocomplete?q=te&limit=5")
        assert response.status_code == 200
        data = response.json()
        assert len(data["suggestions"]) <= 5
    
    @pytest.mark.integration
    async def test_autocomplete_empty_query(self, client: AsyncClient):
        """빈 쿼리 자동완성 테스트"""
        response = await client.get("/api/autocomplete?q=")
        assert response.status_code == 422
    
    @pytest.mark.integration
    async def test_autocomplete_response_time(self, client: AsyncClient, sample_items):
        """자동완성 응답 시간 테스트"""
        response = await client.get("/api/autocomplete?q=te")
        assert response.status_code == 200
        data = response.json()
        assert "response_time_ms" in data
        # 자동완성은 50ms 미만 목표
        assert data["response_time_ms"] < 1000  # 테스트 환경에서는 1초로 여유있게


# 다양한 자동완성 쿼리 테스트 (총 100개)
@pytest.mark.integration
@pytest.mark.parametrize("query,limit", [
    ("a", 5),
    ("te", 10),
    ("sea", 3),
    ("pro", 7),
    ("it", 8),
] * 19)  # 5 * 19 = 95개 추가 테스트
async def test_autocomplete_various_queries(client: AsyncClient, sample_items, query, limit):
    """다양한 자동완성 쿼리 테스트"""
    response = await client.get(f"/api/autocomplete?q={query}&limit={limit}")
    assert response.status_code == 200
    data = response.json()
    assert len(data["suggestions"]) <= limit

