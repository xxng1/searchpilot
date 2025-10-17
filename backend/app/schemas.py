from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class SearchItemBase(BaseModel):
    """검색 아이템 기본 스키마"""
    title: str
    description: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[str] = None
    price: Optional[float] = None
    popularity: int = 0


class SearchItemCreate(SearchItemBase):
    """검색 아이템 생성 스키마"""
    pass


class SearchItem(SearchItemBase):
    """검색 아이템 응답 스키마"""
    id: int
    created_at: datetime
    updated_at: datetime
    highlight: Optional[str] = None
    
    class Config:
        from_attributes = True


class SearchQuery(BaseModel):
    """검색 쿼리 스키마"""
    q: str = Field(..., min_length=1, max_length=255, description="검색 키워드")
    category: Optional[str] = Field(None, description="카테고리 필터")
    min_price: Optional[float] = Field(None, ge=0, description="최소 가격")
    max_price: Optional[float] = Field(None, ge=0, description="최대 가격")
    sort: str = Field("relevance", description="정렬 기준 (relevance, date, popularity, price)")
    order: str = Field("desc", description="정렬 순서 (asc, desc)")
    page: int = Field(1, ge=1, description="페이지 번호")
    size: int = Field(20, ge=1, le=100, description="페이지 크기")


class SearchResponse(BaseModel):
    """검색 응답 스키마"""
    query: str
    total: int
    page: int
    size: int
    total_pages: int
    items: List[SearchItem]
    response_time_ms: float
    facets: Optional[dict] = None
    # 새로운 메타데이터 추가
    search_id: Optional[str] = None
    cache_hit: bool = False
    suggestions: Optional[List[str]] = None


class AutocompleteResponse(BaseModel):
    """자동완성 응답 스키마"""
    suggestions: List[str]
    response_time_ms: float


class SuggestionResponse(BaseModel):
    """추천 검색어 응답 스키마"""
    popular: List[str]
    recent: List[str]


class SearchStats(BaseModel):
    """검색 통계 스키마"""
    total_items: int
    total_searches: int
    avg_response_time_ms: float
    popular_queries: List[dict]


class HealthCheck(BaseModel):
    """헬스체크 응답 스키마"""
    status: str
    version: str
    database: str
    timestamp: datetime


class SearchAnalytics(BaseModel):
    """검색 분석 스키마"""
    query: str
    result_count: int
    response_time_ms: float
    timestamp: datetime
    user_agent: Optional[str] = None
    ip_address: Optional[str] = None


class PopularQueries(BaseModel):
    """인기 검색어 스키마"""
    query: str
    count: int
    last_searched: datetime

