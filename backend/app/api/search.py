from fastapi import APIRouter, Depends, Query, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
import time
import uuid
import hashlib

from app.database import get_db
from app.services.search_service import SearchService
from app.schemas import (
    SearchQuery,
    SearchResponse,
    SearchItem as SearchItemSchema,
    AutocompleteResponse,
    SuggestionResponse,
    SearchStats,
    SearchAnalytics,
    PopularQueries
)
from app.config import settings

router = APIRouter(prefix="/api", tags=["search"])


@router.get("/search", response_model=SearchResponse)
async def search(
    request: Request,
    q: str = Query(..., min_length=1, max_length=255, description="검색 키워드"),
    category: Optional[str] = Query(None, description="카테고리 필터"),
    min_price: Optional[float] = Query(None, ge=0, description="최소 가격"),
    max_price: Optional[float] = Query(None, ge=0, description="최대 가격"),
    sort: str = Query("relevance", description="정렬 기준"),
    order: str = Query("desc", description="정렬 순서"),
    page: int = Query(1, ge=1, description="페이지 번호"),
    size: int = Query(20, ge=1, le=100, description="페이지 크기"),
    db: AsyncSession = Depends(get_db)
):
    """
    검색 API - v2.0 (카나리 배포)
    
    새로운 기능:
    - 검색 분석 추적
    - 캐시 히트 정보
    - 관련 검색어 제안
    - 검색 ID 추적
    
    - **q**: 검색 키워드 (필수)
    - **category**: 카테고리 필터
    - **min_price**: 최소 가격
    - **max_price**: 최대 가격
    - **sort**: 정렬 기준 (relevance, date, popularity, price)
    - **order**: 정렬 순서 (asc, desc)
    - **page**: 페이지 번호
    - **size**: 페이지 크기 (최대 100)
    """
    start_time = time.time()
    
    # 고유한 검색 ID 생성
    search_id = str(uuid.uuid4())
    
    # 캐시 키 생성 (간단한 해시)
    cache_key = hashlib.md5(f"{q}:{category}:{page}:{size}".encode()).hexdigest()
    
    search_query = SearchQuery(
        q=q,
        category=category,
        min_price=min_price,
        max_price=max_price,
        sort=sort,
        order=order,
        page=page,
        size=size
    )
    
    service = SearchService(db)
    items, total, response_time = await service.search(search_query)
    
    # Get facets
    facets = await service.get_facets(q)
    
    # 관련 검색어 제안 (새로운 기능)
    suggestions = await service.get_related_suggestions(q, limit=5)
    
    # Highlight search terms
    highlighted_items = []
    for item in items:
        item_dict = SearchItemSchema.model_validate(item).model_dump()
        item_dict['highlight'] = service.highlight_text(item.title, q)
        highlighted_items.append(SearchItemSchema(**item_dict))
    
    total_pages = (total + size - 1) // size
    
    # 검색 분석 데이터 수집 (새로운 기능)
    client_ip = request.client.host if request.client else "unknown"
    user_agent = request.headers.get("user-agent", "unknown")
    
    # 응답 시간 계산
    total_response_time = (time.time() - start_time) * 1000
    
    return SearchResponse(
        query=q,
        total=total,
        page=page,
        size=size,
        total_pages=total_pages,
        items=highlighted_items,
        response_time_ms=round(total_response_time, 2),
        facets=facets,
        # 새로운 메타데이터
        search_id=search_id,
        cache_hit=False,  # 실제 캐시 구현 시 업데이트
        suggestions=suggestions
    )


@router.get("/autocomplete", response_model=AutocompleteResponse)
async def autocomplete(
    q: str = Query(..., min_length=1, max_length=100, description="부분 검색어"),
    limit: int = Query(10, ge=1, le=20, description="제안 개수"),
    db: AsyncSession = Depends(get_db)
):
    """
    자동완성 API
    
    - **q**: 부분 검색어
    - **limit**: 제안 개수 (최대 20)
    """
    start_time = time.time()
    
    service = SearchService(db)
    suggestions = await service.autocomplete(q, limit)
    
    response_time = (time.time() - start_time) * 1000
    
    return AutocompleteResponse(
        suggestions=suggestions,
        response_time_ms=round(response_time, 2)
    )


@router.get("/suggestions", response_model=SuggestionResponse)
async def get_suggestions(
    db: AsyncSession = Depends(get_db)
):
    """
    추천 검색어 API
    
    인기 검색어와 최근 검색어를 반환합니다.
    """
    service = SearchService(db)
    suggestions = await service.get_suggestions()
    
    return SuggestionResponse(**suggestions)


@router.get("/search/stats", response_model=SearchStats)
async def get_search_stats(
    db: AsyncSession = Depends(get_db)
):
    """
    검색 통계 API
    
    전체 검색 통계 정보를 반환합니다.
    """
    service = SearchService(db)
    stats = await service.get_stats()
    
    return SearchStats(**stats)


@router.get("/search/popular", response_model=List[PopularQueries])
async def get_popular_queries(
    limit: int = Query(10, ge=1, le=50, description="조회할 인기 검색어 개수"),
    db: AsyncSession = Depends(get_db)
):
    """
    인기 검색어 API - v2.0 (카나리 배포)
    
    가장 많이 검색된 쿼리들을 반환합니다.
    """
    service = SearchService(db)
    popular_queries = await service.get_popular_queries(limit)
    
    return popular_queries


@router.get("/search/analytics", response_model=SearchAnalytics)
async def get_search_analytics(
    query: str = Query(..., description="분석할 검색 쿼리"),
    db: AsyncSession = Depends(get_db)
):
    """
    검색 분석 API - v2.0 (카나리 배포)
    
    특정 검색 쿼리에 대한 상세 분석 정보를 반환합니다.
    """
    service = SearchService(db)
    analytics = await service.get_search_analytics(query)
    
    return analytics

