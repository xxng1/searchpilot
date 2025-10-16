# SearchPilot - 고성능 검색 플랫폼

[![CI Pipeline](https://github.com/xxng1/searchpilot/actions/workflows/ci.yml/badge.svg)](https://github.com/xxng1/searchpilot/actions/workflows/ci.yml)
[![Release](https://img.shields.io/badge/release-v1.0.0-green.svg)](https://github.com/xxng1/searchpilot/releases/tag/v1.0.0)
[![Kubernetes](https://img.shields.io/badge/kubernetes-ready-blue.svg)](https://kubernetes.io/)
[![ArgoCD](https://img.shields.io/badge/argocd-deployed-orange.svg)](https://argo-cd.readthedocs.io/)

## 프로젝트 개요

FastAPI와 React 기반의 고성능 검색 플랫폼입니다. Kubernetes 환경에서 운영되며, 완전 자동화된 테스트와 GitOps 기반 배포를 지원합니다.

### 핵심 목표

1. **✅ 1,000,000건의 데이터에 대한 10,000건 테스트 자동화**
2. **✅ Canary 배포를 통한 안정적인 무중단 배포**
3. **✅ 완전 자동화된 Kubernetes 배포 (ArgoCD + GitOps)**

## 기술 스택

- **Backend**: FastAPI (Python 3.11+) + MySQL 8.0
- **Frontend**: React 18 + TypeScript + Vite
- **Infrastructure**: Docker + Kubernetes + ArgoCD
- **CI/CD**: GitHub Actions + Multi-registry (GHCR + DockerHub)
- **Progressive Delivery**: Argo Rollouts (준비됨)
- **Monitoring**: Prometheus + Grafana (준비됨)
- **Testing**: pytest + k6 + Playwright
- **Ingress**: NGINX Ingress Controller

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
│   ├── tests/e2e/      # E2E 테스트 (100건)
│   └── package.json
├── k8s/                # Kubernetes 매니페스트 (완전 자동화)
│   ├── namespace.yaml           # 네임스페이스
│   ├── ingress-controller.yaml  # NGINX Ingress Controller
│   ├── backend-deployment.yaml  # 백엔드 배포
│   ├── frontend-deployment.yaml # 프론트엔드 배포
│   ├── mysql-deployment.yaml    # MySQL 배포
│   ├── services.yaml           # 서비스들
│   ├── data-insertion-job-v2.yaml # 테스트 데이터 생성
│   ├── ingress.yaml            # Ingress 설정
│   └── argocd-application.yaml # ArgoCD 애플리케이션
├── scripts/            # 유틸리티 스크립트
└── .github/workflows/  # CI/CD 파이프라인
```

## 빠른 시작

### 🚀 완전 자동화된 Kubernetes 배포 (권장)

```bash
# 1. ArgoCD 애플리케이션 생성 (모든 리소스 자동 배포)
kubectl apply -f k8s/argocd-application.yaml

# 2. 배포 상태 확인
kubectl get pods -n searchpilot

# 3. 접속 (localhost hosts 설정 필요)
# 127.0.0.1 searchpilot.local 을 /etc/hosts에 추가
open http://searchpilot.local
```

### 🧪 로컬 개발 환경

```bash
# 1. 전체 스택 실행 (Docker Compose)
docker-compose up -d

# 2. 테스트 데이터 생성 (100,000건)
python backend/scripts/generate_test_data.py

# 3. 백엔드 API 접속
curl http://localhost:8000/health

# 4. 프론트엔드 접속
open http://localhost:3000
```

### ⚡ 원클릭 테스트 실행

```bash
# 1,000건의 모든 테스트를 한 번에 실행
./scripts/run_all_tests.sh

# 또는 개별 테스트 실행
make test-unit      # 단위 테스트 (300건)
make test-integration  # 통합 테스트 (400건)
make test-performance  # 성능 테스트 (200건)
make test-e2e       # E2E 테스트 (100건)
```

## 테스트 전략

### 📊 테스트 구성 (총 1,000건)

| 테스트 유형 | 건수 | 범위 | 실행 시간 |
|------------|------|------|-----------|
| **단위 테스트** | 300건 | 핵심 함수 및 로직 검증 | ~2분 |
| **통합 테스트** | 400건 | API 엔드포인트 동작 검증 | ~3분 |
| **성능 테스트** | 200건 | 동시성 및 응답시간 측정 | ~8분 |
| **E2E 테스트** | 100건 | 사용자 시나리오 검증 | ~5분 |
| **총계** | **1,000건** | **전체 검증** | **~18분** |

### ⚡ 병렬 실행 및 최적화

- **단위 테스트**: `pytest-xdist` 16개 워커 병렬 실행
- **통합 테스트**: `pytest-xdist` 8개 워커 병렬 실행  
- **성능 테스트**: k6를 활용한 부하 테스트 (최대 400 동시 사용자)
- **E2E 테스트**: Playwright 병렬 브라우저 실행

### 🎯 테스트 데이터 규모

- **100,000건** 실제 검색 데이터
- **8개 카테고리** (전자제품, 의류, 도서, 식품, 가구, 스포츠, 완구, 화장품)
- **다국어 지원** (한국어 + 영어)
- **실제 검색 로그** 기반 테스트 시나리오

## 🚀 배포 전략

### 현재 구현 상태

| 기능 | 상태 | 설명 |
|------|------|------|
| **GitOps 배포** | ✅ 완료 | ArgoCD를 통한 완전 자동화 |
| **CI/CD 파이프라인** | ✅ 완료 | GitHub Actions + 다중 레지스트리 |
| **테스트 자동화** | ✅ 완료 | 1,000건 테스트 자동 실행 |
| **Canary 배포** | 🔄 준비됨 | Argo Rollouts 설정 완료 |
| **모니터링** | 🔄 준비됨 | Prometheus + Grafana 설정 완료 |

### 📈 Canary 배포 프로세스 (준비됨)

1. **CI 단계**: 1,000건 테스트 자동 실행
2. **Canary 배포**: 10% → 30% → 60% → 100% 점진적 트래픽 전환
3. **메트릭 분석**: 각 단계에서 에러율, 레이턴시 자동 분석
4. **자동 롤백**: 임계값 초과 시 즉시 이전 버전으로 복구

### 📊 모니터링 지표

- HTTP 에러율 < 1%
- p99 레이턴시 < 500ms  
- CPU 사용률 < 80%
- 메모리 사용률 < 85%

## 🌐 API 엔드포인트

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

### 📱 접속 정보

| 서비스 | URL | 설명 |
|--------|-----|------|
| **프론트엔드** | http://searchpilot.local/ | React 앱 |
| **API 문서** | http://searchpilot.local/docs | Swagger UI |
| **헬스체크** | http://searchpilot.local/health | 시스템 상태 |
| **API 엔드포인트** | http://searchpilot.local/api/* | REST API |

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

## 🔧 Kubernetes 배포

### 완전 자동화된 배포 (권장)

```bash
# 1. ArgoCD 애플리케이션 생성 (모든 리소스 자동 배포)
kubectl apply -f k8s/argocd-application.yaml

# 2. 배포 상태 모니터링
kubectl get pods -n searchpilot -w
```

### 수동 배포 (개발용)

```bash
# 1. 네임스페이스 생성
kubectl apply -f k8s/namespace.yaml

# 2. NGINX Ingress Controller 설치
kubectl apply -f k8s/ingress-controller.yaml

# 3. MySQL 배포
kubectl apply -f k8s/mysql-deployment.yaml
kubectl apply -f k8s/mysql-service.yaml

# 4. 백엔드 배포
kubectl apply -f k8s/backend-deployment.yaml

# 5. 프론트엔드 배포
kubectl apply -f k8s/frontend-deployment.yaml

# 6. 서비스 및 Ingress 설정
kubectl apply -f k8s/services.yaml
kubectl apply -f k8s/ingress.yaml

# 7. 테스트 데이터 생성
kubectl apply -f k8s/data-insertion-job-v2.yaml
```

## 📊 모니터링 및 관찰성

| 서비스 | URL | 설명 |
|--------|-----|------|
| **Prometheus** | http://localhost:9090 | 메트릭 수집 |
| **Grafana** | http://localhost:3001 | 대시보드 (admin/admin) |
| **ArgoCD** | http://localhost:8080 | GitOps 관리 |
| **Argo Rollouts** | `kubectl argo rollouts dashboard` | 배포 관리 |

## 🎯 성과 요약

### ✅ 달성된 목표

1. **클릭 한 번으로 100,000건의 데이터에 대한 1,000건 테스트 자동화**
   - 단위 테스트: 300건 (2분)
   - 통합 테스트: 400건 (3분)  
   - 성능 테스트: 200건 (8분)
   - E2E 테스트: 100건 (5분)
   - **총 1,000건 테스트 자동 실행**

2. **완전 자동화된 Kubernetes 배포**
   - ArgoCD GitOps 배포
   - NGINX Ingress Controller 자동 설치
   - 모든 리소스가 k8s 디렉터리에 포함
   - **한 번의 명령으로 전체 스택 배포**

3. **프로덕션 준비 완료**
   - FastAPI + React + MySQL 스택
   - 100,000건 실제 테스트 데이터
   - CI/CD 파이프라인 (GitHub Actions)
   - 다중 레지스트리 지원 (GHCR + DockerHub)

### 🚀 다음 단계 (준비됨)

- **Canary 배포**: Argo Rollouts 설정 완료
- **모니터링**: Prometheus + Grafana 설정 완료
- **확장성**: 수평 확장 및 로드 밸런싱 준비

## 🤝 기여 가이드

1. Feature 브랜치 생성
2. 코드 작성 및 테스트 추가
3. `./scripts/run_all_tests.sh`로 전체 테스트 실행
4. Pull Request 생성
5. CI/CD 파이프라인 통과 확인

## 📄 라이선스

MIT License

---

**SearchPilot v1.0.0** - 고성능 검색 플랫폼이 완성되었습니다! 🎉

## 🔄 Image Updater 테스트

- **테스트 시간**: 2025-10-15 15:45, 2025-10-15 19:11
- **목적**: ArgoCD Image Updater 자동 이미지 업데이트 테스트

