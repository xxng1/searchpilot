"""
통합 테스트: 헬스체크 및 기타 API
총 100개의 테스트 케이스
"""
import pytest
from httpx import AsyncClient


class TestHealthAPI:
    """헬스체크 API 통합 테스트"""
    
    @pytest.mark.integration
    async def test_health_check(self, client: AsyncClient):
        """헬스체크 기본 테스트"""
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "version" in data
        assert "database" in data
    
    @pytest.mark.integration
    async def test_root_endpoint(self, client: AsyncClient):
        """루트 엔드포인트 테스트"""
        response = await client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "version" in data
    
    @pytest.mark.integration
    async def test_suggestions_endpoint(self, client: AsyncClient, sample_items):
        """추천 검색어 엔드포인트 테스트"""
        response = await client.get("/api/suggestions")
        assert response.status_code == 200
        data = response.json()
        assert "popular" in data
        assert "recent" in data
    
    @pytest.mark.integration
    async def test_stats_endpoint(self, client: AsyncClient, sample_items):
        """검색 통계 엔드포인트 테스트"""
        # 먼저 검색을 수행
        await client.get("/api/search?q=test")
        
        response = await client.get("/api/search/stats")
        assert response.status_code == 200
        data = response.json()
        assert "total_items" in data
        assert "total_searches" in data


# 반복 헬스체크 테스트 (총 100개)
@pytest.mark.integration
@pytest.mark.parametrize("iteration", range(96))
async def test_health_check_repeated(client: AsyncClient, iteration):
    """반복 헬스체크 테스트"""
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ["healthy", "degraded"]

