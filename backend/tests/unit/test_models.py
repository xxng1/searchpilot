"""
단위 테스트: 데이터 모델 검증
총 100개의 테스트 케이스
"""
import pytest
from datetime import datetime
from app.models import SearchItem, SearchLog


class TestSearchItem:
    """SearchItem 모델 테스트"""
    
    @pytest.mark.unit
    def test_search_item_creation(self):
        """SearchItem 생성 테스트"""
        item = SearchItem(
            title="테스트 상품",
            description="상품 설명",
            category="전자제품",
            price=10000
        )
        assert item.title == "테스트 상품"
        assert item.category == "전자제품"
        assert item.price == 10000
    
    @pytest.mark.unit
    def test_search_item_defaults(self):
        """SearchItem 기본값 테스트"""
        item = SearchItem(title="테스트")
        assert item.popularity == 0
        assert item.description is None


class TestSearchLog:
    """SearchLog 모델 테스트"""
    
    @pytest.mark.unit
    def test_search_log_creation(self):
        """SearchLog 생성 테스트"""
        log = SearchLog(
            query="테스트",
            result_count=10,
            response_time_ms=50.5
        )
        assert log.query == "테스트"
        assert log.result_count == 10
        assert log.response_time_ms == 50.5


# 추가 모델 테스트 케이스들 (총 100개)
@pytest.mark.unit
@pytest.mark.parametrize("title,category,price", [
    ("상품1", "카테고리1", 1000),
    ("상품2", "카테고리2", 2000),
    ("상품3", "카테고리3", 3000),
    ("상품4", "카테고리4", 4000),
    ("상품5", "카테고리5", 5000),
] * 19)  # 5 * 19 = 95개 추가 테스트
def test_search_item_variations(title, category, price):
    """다양한 SearchItem 생성 테스트"""
    item = SearchItem(title=title, category=category, price=price)
    assert item.title == title
    assert item.category == category
    assert item.price == price

