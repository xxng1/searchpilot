from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_, and_, text, desc
from typing import List, Tuple, Optional
from app.models import SearchItem, SearchLog
from app.schemas import SearchQuery, PopularQueries, SearchAnalytics
import time
import logging
import re
from datetime import datetime

logger = logging.getLogger(__name__)


class SearchService:
    """검색 서비스"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def search(self, query: SearchQuery) -> Tuple[List[SearchItem], int, float]:
        """검색 실행"""
        start_time = time.time()
        
        # Base query with full-text search
        stmt = select(SearchItem)
        
        # Full-text search on title and description
        if query.q:
            search_pattern = f"%{query.q}%"
            stmt = stmt.where(
                or_(
                    SearchItem.title.like(search_pattern),
                    SearchItem.description.like(search_pattern),
                    SearchItem.tags.like(search_pattern)
                )
            )
        
        # Apply filters
        if query.category:
            stmt = stmt.where(SearchItem.category == query.category)
        
        if query.min_price is not None:
            stmt = stmt.where(SearchItem.price >= query.min_price)
        
        if query.max_price is not None:
            stmt = stmt.where(SearchItem.price <= query.max_price)
        
        # Count total results
        count_stmt = select(func.count()).select_from(stmt.subquery())
        result = await self.db.execute(count_stmt)
        total = result.scalar()
        
        # Apply sorting
        if query.sort == "date":
            stmt = stmt.order_by(
                SearchItem.created_at.desc() if query.order == "desc" 
                else SearchItem.created_at.asc()
            )
        elif query.sort == "popularity":
            stmt = stmt.order_by(
                SearchItem.popularity.desc() if query.order == "desc"
                else SearchItem.popularity.asc()
            )
        elif query.sort == "price":
            stmt = stmt.order_by(
                SearchItem.price.desc() if query.order == "desc"
                else SearchItem.price.asc()
            )
        else:  # relevance (default)
            stmt = stmt.order_by(SearchItem.popularity.desc())
        
        # Apply pagination
        offset = (query.page - 1) * query.size
        stmt = stmt.offset(offset).limit(query.size)
        
        # Execute query
        result = await self.db.execute(stmt)
        items = result.scalars().all()
        
        # Calculate response time
        response_time = (time.time() - start_time) * 1000
        
        # Log search
        await self._log_search(query.q, total, response_time)
        
        return items, total, response_time
    
    async def autocomplete(self, partial_query: str, limit: int = 10) -> List[str]:
        """자동완성 제안"""
        stmt = select(SearchItem.title).where(
            SearchItem.title.like(f"{partial_query}%")
        ).distinct().limit(limit)
        
        result = await self.db.execute(stmt)
        suggestions = [row[0] for row in result.fetchall()]
        
        return suggestions
    
    async def get_suggestions(self, popular_limit: int = 5, recent_limit: int = 5) -> dict:
        """추천 검색어 가져오기"""
        # Popular queries
        popular_stmt = select(
            SearchLog.query,
            func.count(SearchLog.id).label('count')
        ).group_by(
            SearchLog.query
        ).order_by(
            func.count(SearchLog.id).desc()
        ).limit(popular_limit)
        
        result = await self.db.execute(popular_stmt)
        popular = [row[0] for row in result.fetchall()]
        
        # Recent queries - using subquery to avoid DISTINCT/ORDER BY conflict
        recent_stmt = select(
            SearchLog.query,
            func.max(SearchLog.created_at).label('last_search')
        ).group_by(
            SearchLog.query
        ).order_by(
            func.max(SearchLog.created_at).desc()
        ).limit(recent_limit)
        
        result = await self.db.execute(recent_stmt)
        recent = [row[0] for row in result.fetchall()]
        
        return {
            "popular": popular,
            "recent": recent
        }
    
    async def get_stats(self) -> dict:
        """검색 통계 가져오기"""
        # Total items
        total_items_stmt = select(func.count(SearchItem.id))
        result = await self.db.execute(total_items_stmt)
        total_items = result.scalar()
        
        # Total searches
        total_searches_stmt = select(func.count(SearchLog.id))
        result = await self.db.execute(total_searches_stmt)
        total_searches = result.scalar()
        
        # Average response time
        avg_time_stmt = select(func.avg(SearchLog.response_time_ms))
        result = await self.db.execute(avg_time_stmt)
        avg_response_time = result.scalar() or 0
        
        # Popular queries
        popular_stmt = select(
            SearchLog.query,
            func.count(SearchLog.id).label('count'),
            func.avg(SearchLog.response_time_ms).label('avg_time')
        ).group_by(
            SearchLog.query
        ).order_by(
            func.count(SearchLog.id).desc()
        ).limit(10)
        
        result = await self.db.execute(popular_stmt)
        popular_queries = [
            {
                "query": row[0],
                "count": row[1],
                "avg_time_ms": round(row[2], 2) if row[2] else 0
            }
            for row in result.fetchall()
        ]
        
        return {
            "total_items": total_items,
            "total_searches": total_searches,
            "avg_response_time_ms": round(avg_response_time, 2),
            "popular_queries": popular_queries
        }
    
    async def get_facets(self, query: str) -> dict:
        """패싯 정보 가져오기 (카테고리별 아이템 수)"""
        search_pattern = f"%{query}%"
        
        stmt = select(
            SearchItem.category,
            func.count(SearchItem.id).label('count')
        ).where(
            or_(
                SearchItem.title.like(search_pattern),
                SearchItem.description.like(search_pattern)
            )
        ).group_by(
            SearchItem.category
        ).order_by(
            func.count(SearchItem.id).desc()
        )
        
        result = await self.db.execute(stmt)
        facets = {row[0]: row[1] for row in result.fetchall() if row[0]}
        
        return {"categories": facets}
    
    def highlight_text(self, text: str, query: str) -> str:
        """검색어 하이라이트"""
        if not text or not query:
            return text
        
        # Escape special regex characters
        escaped_query = re.escape(query)
        pattern = re.compile(f"({escaped_query})", re.IGNORECASE)
        
        return pattern.sub(r"<mark>\1</mark>", text)
    
    async def _log_search(self, query: str, result_count: int, response_time_ms: float):
        """검색 로그 저장"""
        try:
            log = SearchLog(
                query=query,
                result_count=result_count,
                response_time_ms=response_time_ms
            )
            self.db.add(log)
            await self.db.commit()
        except Exception as e:
            logger.error(f"Failed to log search: {e}")
            await self.db.rollback()

    async def get_related_suggestions(self, query: str, limit: int = 5) -> List[str]:
        """관련 검색어 제안 (새로운 기능 - 카나리 배포)"""
        try:
            # 유사한 검색어 찾기 (간단한 구현)
            stmt = select(SearchLog.query, func.count(SearchLog.query).label('count'))\
                .where(SearchLog.query != query)\
                .where(SearchLog.query.like(f"%{query[:3]}%"))\
                .group_by(SearchLog.query)\
                .order_by(desc('count'))\
                .limit(limit)
            
            result = await self.db.execute(stmt)
            suggestions = [row[0] for row in result.fetchall()]
            
            # 기본 제안어가 부족하면 일반적인 제안어 추가
            if len(suggestions) < limit:
                default_suggestions = ["인기 상품", "할인 상품", "신상품", "베스트셀러", "추천 상품"]
                for suggestion in default_suggestions:
                    if suggestion not in suggestions and len(suggestions) < limit:
                        suggestions.append(suggestion)
            
            return suggestions[:limit]
        except Exception as e:
            logger.error(f"Failed to get related suggestions: {e}")
            return []

    async def get_popular_queries(self, limit: int = 10) -> List[PopularQueries]:
        """인기 검색어 조회 (새로운 기능 - 카나리 배포)"""
        try:
            stmt = select(
                SearchLog.query,
                func.count(SearchLog.query).label('count'),
                func.max(SearchLog.created_at).label('last_searched')
            )\
                .group_by(SearchLog.query)\
                .order_by(desc('count'))\
                .limit(limit)
            
            result = await self.db.execute(stmt)
            popular_queries = []
            
            for row in result.fetchall():
                popular_queries.append(PopularQueries(
                    query=row[0],
                    count=row[1],
                    last_searched=row[2]
                ))
            
            return popular_queries
        except Exception as e:
            logger.error(f"Failed to get popular queries: {e}")
            return []

    async def get_search_analytics(self, query: str) -> SearchAnalytics:
        """검색 분석 정보 조회 (새로운 기능 - 카나리 배포)"""
        try:
            # 해당 쿼리의 검색 통계 조회
            stmt = select(
                func.count(SearchLog.id).label('total_searches'),
                func.avg(SearchLog.response_time_ms).label('avg_response_time'),
                func.max(SearchLog.created_at).label('last_searched')
            ).where(SearchLog.query == query)
            
            result = await self.db.execute(stmt)
            row = result.fetchone()
            
            # 결과 개수 조회
            count_stmt = select(func.count()).where(SearchItem.title.like(f"%{query}%"))
            count_result = await self.db.execute(count_stmt)
            result_count = count_result.scalar() or 0
            
            return SearchAnalytics(
                query=query,
                result_count=result_count,
                response_time_ms=float(row[1] or 0),
                timestamp=row[2] or datetime.now(),
                user_agent=None,  # 실제 구현 시 추가
                ip_address=None   # 실제 구현 시 추가
            )
        except Exception as e:
            logger.error(f"Failed to get search analytics: {e}")
            return SearchAnalytics(
                query=query,
                result_count=0,
                response_time_ms=0.0,
                timestamp=datetime.now()
            )

