# 기여 가이드

SearchPilot 프로젝트에 기여해주셔서 감사합니다! 🎉

## 기여 방법

### 1. 이슈 생성

버그 리포트나 기능 제안은 GitHub Issues를 통해 생성해주세요.

#### 버그 리포트 템플릿
```markdown
**버그 설명**
버그에 대한 명확하고 간결한 설명

**재현 방법**
1. '...'로 이동
2. '...'를 클릭
3. '...'까지 스크롤
4. 에러 발생

**예상 동작**
예상했던 동작 설명

**스크린샷**
해당되는 경우 스크린샷 추가

**환경**
- OS: [예: Windows 10]
- 브라우저: [예: Chrome 91]
- 버전: [예: 1.0.0]
```

### 2. Pull Request 생성

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### 3. 코드 스타일

#### Python (Backend)
- PEP 8 준수
- Type hints 사용
- Docstring 작성 (Google Style)

```python
def search_items(query: str, limit: int = 20) -> List[SearchItem]:
    """
    검색 쿼리를 실행합니다.
    
    Args:
        query: 검색 키워드
        limit: 최대 결과 수
    
    Returns:
        검색 결과 리스트
    
    Raises:
        ValueError: 쿼리가 비어있는 경우
    """
    pass
```

#### TypeScript (Frontend)
- ESLint 규칙 준수
- 컴포넌트는 함수형으로 작성
- Props는 interface로 정의

```typescript
interface SearchBarProps {
  onSearch: (query: string) => void
  placeholder?: string
}

const SearchBar: React.FC<SearchBarProps> = ({ onSearch, placeholder }) => {
  // ...
}
```

### 4. 테스트 작성

모든 새로운 기능과 버그 수정에는 테스트가 필요합니다.

#### Backend 테스트
```python
@pytest.mark.unit
async def test_search_functionality():
    """검색 기능이 올바르게 동작하는지 테스트"""
    # Arrange
    service = SearchService(db_session)
    
    # Act
    results = await service.search("test query")
    
    # Assert
    assert len(results) > 0
    assert results[0].title is not None
```

#### Frontend 테스트
```typescript
test('검색어 입력 시 자동완성이 표시됨', async ({ page }) => {
  await page.goto('/')
  await page.fill('input[type="text"]', 'test')
  await expect(page.locator('text=자동완성')).toBeVisible()
})
```

### 5. 커밋 메시지 규칙

```
<type>(<scope>): <subject>

<body>

<footer>
```

#### Type
- `feat`: 새로운 기능
- `fix`: 버그 수정
- `docs`: 문서 수정
- `style`: 코드 포맷팅, 세미콜론 누락 등
- `refactor`: 코드 리팩토링
- `test`: 테스트 코드
- `chore`: 빌드 프로세스, 패키지 매니저 등

#### 예시
```
feat(search): 카테고리 필터 기능 추가

- 카테고리별 검색 결과 필터링
- 패싯 검색 지원
- UI 컴포넌트 추가

Closes #123
```

## 개발 환경 설정

### 백엔드 개발

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### 프론트엔드 개발

```bash
cd frontend
npm install
npm run dev
```

### 테스트 실행

```bash
# 전체 테스트
./scripts/run_all_tests.sh

# 백엔드 테스트만
cd backend && pytest

# 프론트엔드 테스트만
cd frontend && npm run test:e2e
```

## 문의

질문이나 도움이 필요하시면 이슈를 생성하거나 이메일로 연락주세요.

