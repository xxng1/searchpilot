from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
import time

from app.database import get_db
from app.services.search_service import SearchService
from app.schemas import (
    SearchQuery,
    SearchResponse,
    SearchItem as SearchItemSchema,
    AutocompleteResponse,
    SuggestionResponse,
    SearchStats
)
from app.config import settings

router = APIRouter(prefix="/api", tags=["search"])


@router.get("/search", response_model=SearchResponse)
async def search(
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
    검색 API
    
    - **q**: 검색 키워드 (필수)
    - **category**: 카테고리 필터
    - **min_price**: 최소 가격
    - **max_price**: 최대 가격
    - **sort**: 정렬 기준 (relevance, date, popularity, price)
    - **order**: 정렬 순서 (asc, desc)
    - **page**: 페이지 번호
    - **size**: 페이지 크기 (최대 100)
    """
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
    
    # Highlight search terms
    highlighted_items = []
    for item in items:
        item_dict = SearchItemSchema.model_validate(item).model_dump()
        item_dict['highlight'] = service.highlight_text(item.title, q)
        highlighted_items.append(SearchItemSchema(**item_dict))
    
    total_pages = (total + size - 1) // size
    
    return SearchResponse(
        query=q,
        total=total,
        page=page,
        size=size,
        total_pages=total_pages,
        items=highlighted_items,
        response_time_ms=round(response_time, 2),
        facets=facets
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

