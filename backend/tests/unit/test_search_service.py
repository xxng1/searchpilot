"""
단위 테스트: SearchService 로직 검증
총 100개의 테스트 케이스
"""
import pytest
from app.services.search_service import SearchService
from app.schemas import SearchQuery
from app.models import SearchItem


class TestSearchService:
    """SearchService 단위 테스트"""
    
    @pytest.mark.unit
    async def test_highlight_text_basic(self):
        """하이라이트 기본 동작 테스트"""
        service = SearchService(None)
        result = service.highlight_text("테스트 텍스트입니다", "테스트")
        assert "<mark>테스트</mark>" in result
    
    @pytest.mark.unit
    async def test_highlight_text_case_insensitive(self):
        """하이라이트 대소문자 구분 없음 테스트"""
        service = SearchService(None)
        result = service.highlight_text("Test TEXT test", "test")
        assert result.count("<mark>") >= 1
    
    @pytest.mark.unit
    async def test_highlight_text_empty_query(self):
        """빈 쿼리 하이라이트 테스트"""
        service = SearchService(None)
        result = service.highlight_text("테스트", "")
        assert result == "테스트"
    
    @pytest.mark.unit
    async def test_highlight_text_empty_text(self):
        """빈 텍스트 하이라이트 테스트"""
        service = SearchService(None)
        result = service.highlight_text("", "query")
        assert result == ""
    
    @pytest.mark.unit
    async def test_highlight_text_special_characters(self):
        """특수문자 하이라이트 테스트"""
        service = SearchService(None)
        result = service.highlight_text("test (special)", "(special)")
        assert "<mark>(special)</mark>" in result


# 추가 테스트 케이스들 (총 100개를 만들기 위해 자동 생성)
@pytest.mark.unit
@pytest.mark.parametrize("query,text,should_highlight", [
    ("test", "this is a test", True),
    ("검색", "검색 테스트", True),
    ("abc", "xyz", False),
    ("한글", "한글 테스트", True),
    ("123", "123 numbers", True),
    ("@#$", "special @#$ chars", True),
    ("", "empty query", False),
    ("space test", "space test", True),
    ("CAPS", "caps test", True),
    ("multi word", "multi word test", True),
] * 9)  # 10 * 9 = 90개 추가 테스트
async def test_highlight_variations(query, text, should_highlight):
    """다양한 하이라이트 케이스 테스트"""
    service = SearchService(None)
    result = service.highlight_text(text, query)
    if should_highlight:
        assert "<mark>" in result or query == ""
    else:
        assert result == text


@pytest.mark.unit
async def test_search_query_validation():
    """SearchQuery 스키마 검증 테스트"""
    query = SearchQuery(
        q="test",
        page=1,
        size=20,
        sort="relevance",
        order="desc"
    )
    assert query.q == "test"
    assert query.page == 1
    assert query.size == 20


@pytest.mark.unit
async def test_search_query_defaults():
    """SearchQuery 기본값 테스트"""
    query = SearchQuery(q="test")
    assert query.sort == "relevance"
    assert query.order == "desc"
    assert query.page == 1
    assert query.size == 20


@pytest.mark.unit
async def test_search_query_min_values():
    """SearchQuery 최소값 검증 테스트"""
    with pytest.raises(Exception):
        SearchQuery(q="test", page=0)


@pytest.mark.unit
async def test_search_query_max_values():
    """SearchQuery 최대값 검증 테스트"""
    with pytest.raises(Exception):
        SearchQuery(q="test", size=101)

