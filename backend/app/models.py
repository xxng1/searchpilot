from sqlalchemy import Column, Integer, String, Text, DateTime, Float, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from datetime import datetime

Base = declarative_base()


class SearchItem(Base):
    """검색 대상 아이템 모델"""
    __tablename__ = "search_items"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    category = Column(String(100), nullable=True, index=True)
    tags = Column(String(500), nullable=True)
    price = Column(Float, nullable=True)
    popularity = Column(Integer, nullable=False, default=0, server_default="0")
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    def __init__(self, **kwargs):
        # Set default value for popularity if not provided
        if 'popularity' not in kwargs:
            kwargs['popularity'] = 0
        super().__init__(**kwargs)
    
    # Full-text search index
    __table_args__ = (
        Index('idx_title_fulltext', 'title', mysql_prefix='FULLTEXT'),
        Index('idx_description_fulltext', 'description', mysql_prefix='FULLTEXT'),
        Index('idx_category_price', 'category', 'price'),
    )


class SearchLog(Base):
    """검색 로그 모델"""
    __tablename__ = "search_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    query = Column(String(255), nullable=False, index=True)
    result_count = Column(Integer, default=0)
    response_time_ms = Column(Float, nullable=True)
    created_at = Column(DateTime, default=func.now(), index=True)

