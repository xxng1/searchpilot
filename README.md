# SearchPilot - 고성능 검색 플랫폼

## 프로젝트 개요

FastAPI와 React 기반의 고성능 검색 플랫폼입니다. Kubernetes 환경에서 운영되며, 자동화된 테스트와 Canary 배포를 지원합니다.

### 핵심 목표

1. **클릭 한 번으로 100,000건의 데이터에 대한 1,000건 테스트 자동화**
2. **Canary 배포를 통한 안정적인 무중단 배포**

## 기술 스택

- **Backend**: FastAPI (Python 3.11+)
- **Frontend**: React 18 + TypeScript
- **Database**: MySQL 8.0
- **Infrastructure**: Docker, Kubernetes
- **CI/CD**: GitHub Actions
- **Progressive Delivery**: Argo Rollouts
- **Monitoring**: Prometheus, Grafana
- **Testing**: pytest, k6, Playwright

## 프로젝트 구조

```
searchpilot/
├── backend/              # FastAPI 백엔드
│   ├── app/
│   │   ├── api/         # API 라우터
│   │   ├── models/      # 데이터베이스 모델
│   │   ├── services/    # 비즈니스 로직
│   │   └── main.py
│   ├── tests/           # 테스트 코드
│   │   ├── unit/        # 단위 테스트 (300건)
│   │   ├── integration/ # 통합 테스트 (400건)
│   │   └── performance/ # 성능 테스트 (200건)
│   └── requirements.txt
├── frontend/            # React 프론트엔드
│   ├── src/
│   ├── tests/          # E2E 테스트 (100건)
│   └── package.json
├── k8s/                # Kubernetes 매니페스트
│   ├── base/           # 기본 리소스
│   ├── canary/         # Canary 배포 설정
│   └── monitoring/     # Prometheus, Grafana
├── scripts/            # 유틸리티 스크립트
└── .github/workflows/  # CI/CD 파이프라인
```

## 빠른 시작

### 로컬 개발 환경

```bash
# 1. 전체 스택 실행 (Docker Compose)
docker-compose up -d

# 2. 테스트 데이터 생성 (100,000건)
python scripts/generate_test_data.py

# 3. 백엔드 API 접속
curl http://localhost:8000/health

# 4. 프론트엔드 접속
open http://localhost:3000
```

### 원클릭 테스트 실행

```bash
# 1,000건의 모든 테스트를 한 번에 실행
./scripts/run_all_tests.sh

# 또는 Make 명령어 사용
make test-all
```

## 테스트 전략

### 테스트 구성 (총 1,000건)

- **단위 테스트** (300건): 핵심 함수 및 로직 검증
- **통합 테스트** (400건): API 엔드포인트 동작 검증
- **성능 테스트** (200건): 동시성 및 응답시간 측정
- **E2E 테스트** (100건): 사용자 시나리오 검증

### 병렬 실행

- `pytest-xdist`를 활용한 16개 워커 병렬 실행
- 전체 테스트 실행 시간: 약 5-10분

## Canary 배포 프로세스

### 배포 단계

1. **CI 단계**: 1,000건 테스트 자동 실행
2. **Canary 배포**: 10% → 30% → 60% → 100% 점진적 트래픽 전환
3. **메트릭 분석**: 각 단계에서 에러율, 레이턴시 자동 분석
4. **자동 롤백**: 임계값 초과 시 즉시 이전 버전으로 복구

### 모니터링 지표

- HTTP 에러율 < 1%
- p99 레이턴시 < 500ms
- CPU 사용률 < 80%
- 메모리 사용률 < 85%

## API 엔드포인트

### 검색 API

```bash
# 기본 검색
GET /api/search?q={query}&page=1&size=20

# 자동완성
GET /api/autocomplete?q={partial_query}

# 추천 검색어
GET /api/suggestions

# 검색 통계
GET /api/search/stats

# 헬스체크
GET /health
```

## 개발 가이드

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
# 단위 테스트
pytest tests/unit -v

# 통합 테스트
pytest tests/integration -v

# 성능 테스트
k6 run tests/performance/load_test.js

# E2E 테스트
cd frontend && npm run test:e2e
```

## Kubernetes 배포

```bash
# 1. 네임스페이스 생성
kubectl create namespace searchpilot

# 2. MySQL 배포
kubectl apply -f k8s/base/mysql/

# 3. 백엔드 배포 (Argo Rollouts)
kubectl apply -f k8s/canary/backend-rollout.yaml

# 4. 프론트엔드 배포
kubectl apply -f k8s/base/frontend/

# 5. 모니터링 스택 배포
kubectl apply -f k8s/monitoring/
```

## 모니터링 및 관찰성

- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3001 (admin/admin)
- **Argo Rollouts Dashboard**: `kubectl argo rollouts dashboard`

## 기여 가이드

1. Feature 브랜치 생성
2. 코드 작성 및 테스트 추가
3. `make test-all`로 전체 테스트 실행
4. Pull Request 생성
5. CI/CD 파이프라인 통과 확인

## 라이선스

MIT License

