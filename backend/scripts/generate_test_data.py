#!/usr/bin/env python3
"""
테스트 데이터 생성 스크립트
MySQL 데이터베이스에 100,000개의 테스트 데이터를 생성합니다.
"""

import asyncio
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from faker import Faker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import os
from datetime import datetime, timedelta
import random

from app.models import Base, SearchItem
from app.config import settings

# Faker 인스턴스 생성 (한국어 + 영어)
fake = Faker(['ko_KR', 'en_US'])
Faker.seed(42)  # 재현 가능한 데이터 생성

# 카테고리 목록
CATEGORIES = [
    '전자제품', '의류', '도서', '식품', '가구', 
    '스포츠', '완구', '화장품', '가전', '악기',
    '자동차용품', '반려동물용품', '문구', '주방용품', '침구'
]

# 인기 검색어 (더 자주 등장하는 키워드)
POPULAR_KEYWORDS = [
    '스마트폰', '노트북', '헤드폰', '키보드', '마우스',
    '청바지', '티셔츠', '운동화', '가방', '지갑',
    '소설', '자기계발', '요리책', '만화', '잡지',
    '과자', '음료', '라면', '커피', '차',
    '책상', '의자', '침대', '소파', '서랍장'
]


async def create_database():
    """데이터베이스 테이블 생성"""
    print("📦 데이터베이스 테이블 생성 중...")
    
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    
    await engine.dispose()
    print("✅ 테이블 생성 완료")


async def generate_items(count: int = 100000, batch_size: int = 1000):
    """검색 아이템 생성"""
    print(f"🔄 {count:,}개의 테스트 데이터 생성 중...")
    
    engine = create_async_engine(settings.DATABASE_URL, echo=False, pool_size=20)
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    items = []
    created_count = 0
    
    for i in range(count):
        # 80%는 인기 키워드 포함, 20%는 랜덤
        if random.random() < 0.8:
            keyword = random.choice(POPULAR_KEYWORDS)
            title = f"{keyword} {fake.word()} {fake.word()}"
        else:
            title = fake.sentence(nb_words=random.randint(2, 5)).rstrip('.')
        
        # 태그 생성 (일부는 인기 키워드 포함)
        tags = []
        for _ in range(random.randint(2, 5)):
            if random.random() < 0.5 and POPULAR_KEYWORDS:
                tags.append(random.choice(POPULAR_KEYWORDS))
            else:
                tags.append(fake.word())
        
        # 아이템 생성
        item = SearchItem(
            title=title,
            description=fake.text(max_nb_chars=random.randint(100, 300)),
            category=random.choice(CATEGORIES),
            tags=','.join(tags),
            price=round(random.uniform(1000, 1000000), -2),  # 100원 단위
            popularity=int(random.paretovariate(1.5) * 100),  # 파레토 분포
            created_at=datetime.now() - timedelta(days=random.randint(0, 365)),
        )
        
        items.append(item)
        
        # 배치 단위로 저장
        if len(items) >= batch_size:
            async with async_session() as session:
                session.add_all(items)
                await session.commit()
            
            created_count += len(items)
            progress = (created_count / count) * 100
            print(f"진행: {created_count:,}/{count:,} ({progress:.1f}%)")
            items = []
    
    # 남은 아이템 저장
    if items:
        async with async_session() as session:
            session.add_all(items)
            await session.commit()
        created_count += len(items)
    
    await engine.dispose()
    print(f"✅ 총 {created_count:,}개의 데이터 생성 완료")


async def generate_sample_queries(filename: str = "sample_queries.txt"):
    """샘플 검색 쿼리 생성 (테스트용)"""
    print("📝 샘플 검색 쿼리 생성 중...")
    
    queries = set()
    
    # 인기 키워드 기반 쿼리
    for keyword in POPULAR_KEYWORDS:
        queries.add(keyword)
        queries.add(f"{keyword} 추천")
        queries.add(f"{keyword} 가격")
        queries.add(f"{keyword} 리뷰")
    
    # 카테고리 기반 쿼리
    for category in CATEGORIES:
        queries.add(category)
        queries.add(f"{category} 베스트")
        queries.add(f"{category} 인기")
    
    # 랜덤 쿼리
    for _ in range(500):
        queries.add(fake.word())
        queries.add(fake.sentence(nb_words=2).rstrip('.'))
    
    # 파일로 저장
    script_dir = Path(__file__).parent
    filepath = script_dir / filename
    
    with open(filepath, 'w', encoding='utf-8') as f:
        for query in sorted(queries):
            f.write(f"{query}\n")
    
    print(f"✅ {len(queries):,}개의 샘플 쿼리 생성 완료: {filepath}")


async def verify_data():
    """데이터 검증"""
    print("🔍 데이터 검증 중...")
    
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        from sqlalchemy import select, func
        
        # 총 아이템 수
        result = await session.execute(select(func.count(SearchItem.id)))
        total_items = result.scalar()
        
        # 카테고리별 분포
        result = await session.execute(
            select(SearchItem.category, func.count(SearchItem.id))
            .group_by(SearchItem.category)
        )
        category_dist = dict(result.fetchall())
        
        print(f"\n📊 데이터 통계:")
        print(f"   총 아이템 수: {total_items:,}")
        print(f"\n   카테고리별 분포:")
        for category, count in sorted(category_dist.items(), key=lambda x: x[1], reverse=True):
            print(f"      {category}: {count:,}개")
    
    await engine.dispose()
    print("\n✅ 데이터 검증 완료")


async def main():
    """메인 함수"""
    print("=" * 60)
    print("🚀 SearchPilot 테스트 데이터 생성기")
    print("=" * 60)
    print()
    
    # 1. 데이터베이스 초기화
    await create_database()
    print()
    
    # 2. 테스트 데이터 생성
    count = int(os.getenv('TEST_DATA_COUNT', '100000'))
    await generate_items(count=count, batch_size=1000)
    print()
    
    # 3. 샘플 쿼리 생성
    await generate_sample_queries()
    print()
    
    # 4. 데이터 검증
    await verify_data()
    print()
    
    print("=" * 60)
    print("🎉 모든 작업이 완료되었습니다!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())

