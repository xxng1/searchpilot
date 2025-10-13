# SearchPilot 배포 가이드

## 목차

1. [로컬 개발 환경 설정](#로컬-개발-환경-설정)
2. [Kubernetes 클러스터 배포](#kubernetes-클러스터-배포)
3. [Canary 배포 프로세스](#canary-배포-프로세스)
4. [모니터링 설정](#모니터링-설정)
5. [트러블슈팅](#트러블슈팅)

---

## 로컬 개발 환경 설정

### 사전 요구사항

- Docker Desktop (Kubernetes 활성화)
- Python 3.11+
- Node.js 20+
- k6 (성능 테스트)
- kubectl

### 1단계: Docker Compose로 전체 스택 실행

```bash
# 전체 서비스 실행 (MySQL, Backend, Frontend, Prometheus, Grafana)
docker-compose up -d

# 로그 확인
docker-compose logs -f
```

서비스 접속:
- Backend API: http://localhost:8000
- Backend Docs: http://localhost:8000/docs
- Frontend: http://localhost:3000
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3001 (admin/admin)

### 2단계: 테스트 데이터 생성

```bash
# 가상환경 생성 (첫 실행 시)
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt

# 100,000개 데이터 생성
cd ..
python scripts/generate_test_data.py
```

### 3단계: 전체 테스트 실행

```bash
# '딸깍' 한 번으로 1,000건 테스트 실행
./scripts/run_all_tests.sh

# 또는 Makefile 사용
make test-all
```

---

## Kubernetes 클러스터 배포

### 사전 요구사항

- Kubernetes 클러스터 (Minikube, EKS, GKE, AKS 등)
- kubectl 설치 및 구성
- Argo Rollouts 설치
- Ingress Controller (nginx)

### 1단계: Argo Rollouts 설치

```bash
# Argo Rollouts 설치
kubectl create namespace argo-rollouts
kubectl apply -n argo-rollouts -f https://github.com/argoproj/argo-rollouts/releases/latest/download/install.yaml

# Argo Rollouts CLI 설치 (선택사항)
# macOS
brew install argoproj/tap/kubectl-argo-rollouts

# Linux
curl -LO https://github.com/argoproj/argo-rollouts/releases/latest/download/kubectl-argo-rollouts-linux-amd64
chmod +x kubectl-argo-rollouts-linux-amd64
sudo mv kubectl-argo-rollouts-linux-amd64 /usr/local/bin/kubectl-argo-rollouts
```

### 2단계: Nginx Ingress Controller 설치

```bash
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.8.2/deploy/static/provider/cloud/deploy.yaml
```

### 3단계: 네임스페이스 및 기본 리소스 배포

```bash
# 네임스페이스 생성
kubectl apply -f k8s/base/namespace.yaml

# MySQL 배포
kubectl apply -f k8s/base/mysql/mysql-secret.yaml
kubectl apply -f k8s/base/mysql/mysql-pvc.yaml
kubectl apply -f k8s/base/mysql/mysql-deployment.yaml
kubectl apply -f k8s/base/mysql/mysql-service.yaml

# MySQL 준비 대기
kubectl wait --for=condition=ready pod -l app=mysql -n searchpilot --timeout=300s
```

### 4단계: 백엔드 Canary 배포

```bash
# Argo Rollouts 리소스 배포
kubectl apply -f k8s/canary/backend-rollout.yaml
kubectl apply -f k8s/canary/backend-service.yaml
kubectl apply -f k8s/canary/analysis-template.yaml

# 배포 상태 확인
kubectl argo rollouts get rollout backend -n searchpilot --watch
```

### 5단계: 프론트엔드 배포

```bash
kubectl apply -f k8s/base/frontend/frontend-deployment.yaml
kubectl apply -f k8s/base/frontend/frontend-service.yaml
```

### 6단계: Ingress 설정

```bash
kubectl apply -f k8s/base/ingress.yaml

# Ingress 주소 확인
kubectl get ingress -n searchpilot
```

### 7단계: 모니터링 스택 배포

```bash
# Prometheus 배포
kubectl apply -f k8s/monitoring/prometheus-deployment.yaml

# Grafana 배포
kubectl apply -f k8s/monitoring/grafana-deployment.yaml

# 서비스 확인
kubectl get svc -n searchpilot
```

---

## Canary 배포 프로세스

### Canary 배포 단계

SearchPilot는 Argo Rollouts를 사용하여 자동화된 Canary 배포를 수행합니다.

#### 배포 플로우

```
Phase 1: 10% 트래픽 (2분 대기)
   └─> 메트릭 분석 (Success Rate)
        ├─> 통과: Phase 2로 진행
        └─> 실패: 자동 롤백

Phase 2: 30% 트래픽 (2분 대기)
   └─> 메트릭 분석 (Success Rate + Latency)
        ├─> 통과: Phase 3로 진행
        └─> 실패: 자동 롤백

Phase 3: 60% 트래픽 (2분 대기)
   └─> 메트릭 분석 (Success Rate + Latency)
        ├─> 통과: Phase 4로 진행
        └─> 실패: 자동 롤백

Phase 4: 100% 트래픽
   └─> 자동 프로모션 (5분 후)
```

#### 메트릭 임계값

- **Success Rate**: ≥ 99%
- **P99 Latency**: < 500ms
- **Error Rate**: < 1%
- **CPU Usage**: < 80%

### 새 버전 배포

```bash
# 1. 새 이미지 빌드
docker build -t your-registry/backend:v2.0.0 ./backend
docker push your-registry/backend:v2.0.0

# 2. Rollout 이미지 업데이트
kubectl argo rollouts set image backend \
  backend=your-registry/backend:v2.0.0 \
  -n searchpilot

# 3. 배포 상태 실시간 모니터링
kubectl argo rollouts get rollout backend -n searchpilot --watch

# 4. (선택) 수동으로 다음 단계로 진행
kubectl argo rollouts promote backend -n searchpilot

# 5. (선택) 배포 중단 및 롤백
kubectl argo rollouts abort backend -n searchpilot
```

### Argo Rollouts Dashboard

```bash
# Dashboard 실행
kubectl argo rollouts dashboard

# 브라우저에서 접속
open http://localhost:3100
```

---

## 모니터링 설정

### Prometheus

**접속**: `http://prometheus:9090` (클러스터 내부) 또는 포트포워딩

```bash
kubectl port-forward svc/prometheus 9090:9090 -n searchpilot
```

#### 주요 쿼리

```promql
# 요청 성공률
sum(rate(http_requests_total{status=~"2.."}[5m])) / sum(rate(http_requests_total[5m])) * 100

# P99 레이턴시
histogram_quantile(0.99, sum(rate(http_request_duration_seconds_bucket[5m])) by (le)) * 1000

# 에러율
sum(rate(http_requests_total{status=~"5.."}[5m])) / sum(rate(http_requests_total[5m])) * 100

# QPS (Queries Per Second)
sum(rate(http_requests_total[5m]))
```

### Grafana

**접속**: `http://grafana:3000` (클러스터 내부) 또는 포트포워딩

```bash
kubectl port-forward svc/grafana 3000:3000 -n searchpilot
```

**기본 인증정보**: `admin` / `admin`

#### Dashboard 추가

1. Grafana 접속
2. Configuration → Data Sources → Add data source
3. Prometheus 선택
4. URL: `http://prometheus:9090`
5. Save & Test

#### 권장 Dashboard

- **SearchPilot Overview**: 전체 시스템 상태
- **API Performance**: API 성능 메트릭
- **Canary Analysis**: Canary 배포 분석
- **Database Metrics**: MySQL 성능

---

## CI/CD 파이프라인

### GitHub Actions 워크플로우

`.github/workflows/ci-cd.yml` 파일은 다음을 자동화합니다:

1. **테스트 단계** (1,000건 자동 실행)
   - 단위 테스트: 300건
   - 통합 테스트: 400건
   - 성능 테스트: 200건
   - E2E 테스트: 100건

2. **빌드 단계**
   - Docker 이미지 빌드
   - Container Registry에 푸시

3. **배포 단계**
   - Argo Rollouts로 Canary 배포
   - 자동 메트릭 분석
   - 자동 롤백 (실패 시)

### 필요한 Secrets 설정

GitHub Repository → Settings → Secrets and variables → Actions

```
KUBE_CONFIG: Kubernetes 클러스터 접근 설정 (base64 인코딩)
```

kubeconfig 인코딩:
```bash
cat ~/.kube/config | base64
```

---

## 트러블슈팅

### 문제: MySQL 연결 실패

```bash
# MySQL Pod 로그 확인
kubectl logs -l app=mysql -n searchpilot

# MySQL 연결 테스트
kubectl run -it --rm debug --image=mysql:8.0 --restart=Never -n searchpilot -- \
  mysql -h mysql -u searchuser -psearchpass searchpilot
```

### 문제: Canary 배포가 진행되지 않음

```bash
# Rollout 상태 확인
kubectl argo rollouts status backend -n searchpilot

# Analysis Run 확인
kubectl get analysisrun -n searchpilot

# AnalysisRun 로그 확인
kubectl describe analysisrun <analysis-run-name> -n searchpilot
```

### 문제: Prometheus 메트릭이 수집되지 않음

```bash
# Prometheus targets 확인
kubectl port-forward svc/prometheus 9090:9090 -n searchpilot
# 브라우저: http://localhost:9090/targets

# Backend Pod annotations 확인
kubectl get pod -l app=backend -n searchpilot -o yaml | grep -A 5 annotations
```

### 문제: 테스트 실패

```bash
# 테스트 로그 상세 확인
cd backend
pytest tests/unit -v --tb=long

# 특정 테스트만 실행
pytest tests/unit/test_search_service.py::TestSearchService::test_highlight_text_basic -v
```

---

## 성능 튜닝

### Backend 최적화

```yaml
# k8s/canary/backend-rollout.yaml
resources:
  requests:
    memory: "512Mi"
    cpu: "250m"
  limits:
    memory: "1Gi"
    cpu: "500m"

# Replica 수 조정
replicas: 5  # 트래픽에 따라 조정
```

### MySQL 최적화

```yaml
# k8s/base/mysql/mysql-deployment.yaml
resources:
  requests:
    memory: "2Gi"
    cpu: "1000m"
  limits:
    memory: "4Gi"
    cpu: "2000m"
```

### HPA (Horizontal Pod Autoscaler) 설정

```bash
kubectl autoscale rollout backend \
  --min=3 --max=10 \
  --cpu-percent=70 \
  -n searchpilot
```

---

## 추가 리소스

- [Argo Rollouts 문서](https://argoproj.github.io/argo-rollouts/)
- [Prometheus 쿼리 가이드](https://prometheus.io/docs/prometheus/latest/querying/basics/)
- [Grafana Dashboard 가이드](https://grafana.com/docs/grafana/latest/dashboards/)
- [k6 성능 테스트](https://k6.io/docs/)

---

## 문의 및 지원

문제가 발생하거나 질문이 있으시면 이슈를 생성해주세요.

