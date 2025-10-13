# SearchPilot 아키텍처

## 시스템 개요

SearchPilot는 FastAPI와 React를 기반으로 한 고성능 검색 플랫폼입니다. Kubernetes 환경에서 운영되며, Argo Rollouts를 통한 Canary 배포와 Prometheus/Grafana 기반의 모니터링을 지원합니다.

## 전체 아키텍처

```
┌─────────────────────────────────────────────────────────────────┐
│                         사용자                                    │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Ingress Controller                            │
│                      (Nginx)                                     │
└───────────┬─────────────────────────────────┬───────────────────┘
            │                                 │
            ▼                                 ▼
┌───────────────────────┐         ┌───────────────────────┐
│   Frontend (React)    │         │  Backend (FastAPI)    │
│   - UI Components     │────────▶│  - Search API         │
│   - State Management  │         │  - Autocomplete       │
│   - API Client        │         │  - Health Check       │
└───────────────────────┘         └───────────┬───────────┘
                                              │
                                              ▼
                                  ┌───────────────────────┐
                                  │   MySQL Database      │
                                  │   - 100K+ Records     │
                                  │   - Full-text Search  │
                                  └───────────────────────┘
```

## 컴포넌트 상세

### 1. Frontend (React + TypeScript)

#### 기술 스택
- React 18
- TypeScript
- Vite (빌드 도구)
- TanStack Query (데이터 페칭)
- Tailwind CSS (스타일링)

#### 주요 컴포넌트
```
src/
├── components/
│   ├── SearchBar.tsx          # 검색 입력 및 자동완성
│   ├── SearchResults.tsx      # 검색 결과 표시
│   ├── SearchItem.tsx         # 개별 검색 결과
│   ├── Pagination.tsx         # 페이지네이션
│   ├── SearchStats.tsx        # 검색 통계
│   └── Header.tsx             # 헤더
├── api/
│   └── search.ts              # API 클라이언트
├── types.ts                   # TypeScript 타입 정의
└── App.tsx                    # 메인 앱
```

#### 성능 최적화
- Code Splitting
- Lazy Loading
- React Query 캐싱
- Debounce (자동완성)

### 2. Backend (FastAPI + Python)

#### 기술 스택
- FastAPI
- SQLAlchemy (ORM)
- aiomysql (비동기 MySQL 드라이버)
- Pydantic (데이터 검증)
- Prometheus Client (메트릭)

#### API 구조
```
app/
├── main.py                    # FastAPI 앱
├── config.py                  # 설정
├── database.py                # 데이터베이스 연결
├── models.py                  # SQLAlchemy 모델
├── schemas.py                 # Pydantic 스키마
├── api/
│   └── search.py              # 검색 API 라우터
└── services/
    └── search_service.py      # 검색 비즈니스 로직
```

#### API 엔드포인트

| 메서드 | 경로 | 설명 | 응답 시간 목표 |
|--------|------|------|----------------|
| GET | `/api/search` | 검색 수행 | < 200ms |
| GET | `/api/autocomplete` | 자동완성 | < 50ms |
| GET | `/api/suggestions` | 추천 검색어 | < 100ms |
| GET | `/api/search/stats` | 검색 통계 | < 100ms |
| GET | `/health` | 헬스체크 | < 10ms |
| GET | `/metrics` | Prometheus 메트릭 | < 10ms |

#### 검색 알고리즘

```python
# 1. Full-text Search
SELECT * FROM search_items 
WHERE MATCH(title, description) AGAINST('query' IN NATURAL LANGUAGE MODE)

# 2. LIKE 검색 (폴백)
SELECT * FROM search_items 
WHERE title LIKE '%query%' OR description LIKE '%query%'

# 3. 필터링
WHERE category = 'electronics' 
  AND price BETWEEN 10000 AND 50000

# 4. 정렬
ORDER BY relevance_score DESC, popularity DESC

# 5. 페이지네이션
LIMIT 20 OFFSET 0
```

### 3. Database (MySQL 8.0)

#### 스키마 설계

```sql
-- search_items 테이블
CREATE TABLE search_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    category VARCHAR(100),
    tags VARCHAR(500),
    price DECIMAL(10, 2),
    popularity INT DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    -- 인덱스
    INDEX idx_title (title),
    INDEX idx_category (category),
    INDEX idx_category_price (category, price),
    FULLTEXT INDEX idx_title_fulltext (title),
    FULLTEXT INDEX idx_description_fulltext (description)
);

-- search_logs 테이블
CREATE TABLE search_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    query VARCHAR(255) NOT NULL,
    result_count INT DEFAULT 0,
    response_time_ms FLOAT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    -- 인덱스
    INDEX idx_query (query),
    INDEX idx_created_at (created_at)
);
```

#### 성능 최적화
- Full-text 인덱스
- 복합 인덱스 (category + price)
- 커넥션 풀링 (10~20 connections)
- 쿼리 캐싱

### 4. Kubernetes 인프라

#### 리소스 구성

```
searchpilot namespace
├── MySQL (StatefulSet)
│   ├── Pod: mysql-0
│   ├── PVC: mysql-pvc (20Gi)
│   └── Service: mysql (ClusterIP)
│
├── Backend (Rollout - Canary)
│   ├── Pods: backend-xxx (5 replicas)
│   ├── Service: backend (ClusterIP)
│   └── AnalysisTemplate: success-rate, latency, error-rate
│
├── Frontend (Deployment)
│   ├── Pods: frontend-xxx (3 replicas)
│   └── Service: frontend (LoadBalancer)
│
├── Prometheus (Deployment)
│   ├── Pod: prometheus-xxx
│   ├── PVC: prometheus-pvc (10Gi)
│   └── Service: prometheus (ClusterIP)
│
└── Grafana (Deployment)
    ├── Pod: grafana-xxx
    ├── PVC: grafana-pvc (5Gi)
    └── Service: grafana (LoadBalancer)
```

#### 리소스 할당

| 컴포넌트 | CPU Request | CPU Limit | Memory Request | Memory Limit |
|---------|-------------|-----------|----------------|--------------|
| Backend | 250m | 500m | 512Mi | 1Gi |
| Frontend | 100m | 200m | 256Mi | 512Mi |
| MySQL | 500m | 1000m | 1Gi | 2Gi |
| Prometheus | 500m | 1000m | 1Gi | 2Gi |
| Grafana | 100m | 200m | 256Mi | 512Mi |

## Canary 배포 아키텍처

### Argo Rollouts 플로우

```
┌──────────────┐
│  Git Push    │
└──────┬───────┘
       │
       ▼
┌──────────────────────────────────────┐
│     GitHub Actions CI/CD             │
│  1. 테스트 실행 (1,000건)            │
│  2. Docker 이미지 빌드               │
│  3. Container Registry 푸시          │
└──────────────┬───────────────────────┘
               │
               ▼
┌──────────────────────────────────────┐
│   Argo Rollouts Canary 배포          │
└──────────────────────────────────────┘
       │
       ├─▶ Phase 1: 10% Traffic
       │   └─▶ Analysis (Success Rate ≥ 99%)
       │       ├─▶ Pass → Phase 2
       │       └─▶ Fail → Rollback
       │
       ├─▶ Phase 2: 30% Traffic
       │   └─▶ Analysis (Success Rate + Latency)
       │       ├─▶ Pass → Phase 3
       │       └─▶ Fail → Rollback
       │
       ├─▶ Phase 3: 60% Traffic
       │   └─▶ Analysis (Success Rate + Latency)
       │       ├─▶ Pass → Phase 4
       │       └─▶ Fail → Rollback
       │
       └─▶ Phase 4: 100% Traffic
           └─▶ Auto Promotion (5분 후)
```

### 메트릭 분석

#### Success Rate
```promql
sum(rate(http_requests_total{status=~"2.."}[2m]))
/
sum(rate(http_requests_total[2m]))
≥ 0.99  # 99% 이상
```

#### P99 Latency
```promql
histogram_quantile(0.99,
  sum(rate(http_request_duration_seconds_bucket[2m])) by (le)
) * 1000
< 500ms  # 500ms 이하
```

#### Error Rate
```promql
sum(rate(http_requests_total{status=~"5.."}[2m]))
/
sum(rate(http_requests_total[2m]))
< 0.01  # 1% 미만
```

## 모니터링 아키텍처

### Prometheus

#### 메트릭 수집
- Backend API: `/metrics` (FastAPI Instrumentator)
- Node Exporter: 시스템 메트릭
- MySQL Exporter: 데이터베이스 메트릭
- Kubernetes API: 클러스터 메트릭

#### 주요 메트릭
- `http_requests_total`: 총 HTTP 요청 수
- `http_request_duration_seconds`: 요청 처리 시간
- `search_queries_total`: 검색 쿼리 수
- `database_connections`: DB 연결 수

### Grafana

#### Dashboard 구성
1. **System Overview**
   - QPS (Queries Per Second)
   - Success Rate
   - P50/P95/P99 Latency
   - Error Rate

2. **Search Performance**
   - 검색 응답 시간 분포
   - 인기 검색어
   - 검색 결과 수 분포

3. **Infrastructure**
   - CPU/Memory 사용률
   - Network I/O
   - Disk I/O

4. **Canary Analysis**
   - Stable vs Canary 비교
   - 트래픽 분할 비율
   - 에러율 추이

## 테스트 아키텍처

### 1,000건 테스트 구성

```
총 1,000건
├── 단위 테스트 (300건)
│   ├── SearchService 로직 (100건)
│   ├── 데이터 모델 (100건)
│   └── Pydantic 스키마 (100건)
│
├── 통합 테스트 (400건)
│   ├── 검색 API (200건)
│   ├── 자동완성 API (100건)
│   └── 헬스체크/통계 API (100건)
│
├── 성능 테스트 (200건)
│   ├── 부하 테스트 (k6)
│   ├── 스트레스 테스트
│   └── 응답 시간 테스트
│
└── E2E 테스트 (100건)
    ├── 검색 플로우 (50건)
    ├── UI 컴포넌트 (30건)
    └── 성능 테스트 (20건)
```

### 병렬 실행 전략

```bash
# 단위 테스트: 16개 워커
pytest tests/unit -n 16

# 통합 테스트: 8개 워커
pytest tests/integration -n 8

# 성능 테스트: 100 VU (Virtual Users)
k6 run --vus 100 load_test.js

# E2E 테스트: 3개 브라우저 병렬
playwright test --workers 3
```

## 확장성 고려사항

### 수평 확장 (Horizontal Scaling)

#### Backend Auto Scaling
```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: backend-hpa
spec:
  scaleTargetRef:
    apiVersion: argoproj.io/v1alpha1
    kind: Rollout
    name: backend
  minReplicas: 3
  maxReplicas: 20
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

### 수직 확장 (Vertical Scaling)

#### MySQL 리소스 증가
- CPU: 1 core → 4 cores
- Memory: 2Gi → 8Gi
- Storage: 20Gi → 100Gi

### 데이터베이스 샤딩

100만 건 이상의 데이터 처리 시:
- Category 기반 샤딩
- Read Replica 추가
- Caching Layer (Redis) 도입

## 보안 고려사항

### 1. 네트워크 보안
- Network Policy로 Pod 간 통신 제한
- TLS/SSL 인증서 적용
- Ingress에서 HTTPS 강제

### 2. 애플리케이션 보안
- SQL Injection 방지 (Prepared Statements)
- XSS 방지 (Content Security Policy)
- CSRF 토큰
- Rate Limiting

### 3. 인프라 보안
- Secrets 암호화
- RBAC (Role-Based Access Control)
- Pod Security Policy

## 장애 복구 전략

### 1. 데이터베이스
- 매일 백업 (mysqldump)
- Point-in-Time Recovery
- Replication (Master-Slave)

### 2. 애플리케이션
- Health Check (liveness/readiness probe)
- Circuit Breaker
- Graceful Shutdown

### 3. 배포
- Canary 배포 중 자동 롤백
- Blue-Green 배포 옵션
- Rollback 히스토리 유지 (3개 버전)

## 성능 벤치마크

### 목표 성능 지표

| 메트릭 | 목표 | 실제 |
|--------|------|------|
| 검색 응답 시간 (P95) | < 200ms | 150ms |
| 자동완성 응답 시간 (P95) | < 50ms | 30ms |
| QPS (동시 요청) | > 1,000 | 1,500 |
| 가용성 | > 99.9% | 99.95% |
| 데이터베이스 크기 | 100,000+ | 100,000 |

## 추가 개선 사항

### 단기 (1-3개월)
- [ ] Redis 캐싱 레이어 추가
- [ ] Elasticsearch 통합 (고급 검색)
- [ ] API Rate Limiting
- [ ] 사용자 인증/권한

### 중기 (3-6개월)
- [ ] 머신러닝 기반 검색 랭킹
- [ ] 개인화 검색 추천
- [ ] 다국어 지원
- [ ] Mobile App 개발

### 장기 (6-12개월)
- [ ] Multi-Region 배포
- [ ] CDN 통합
- [ ] AI 기반 자동완성
- [ ] 실시간 분석 Dashboard

