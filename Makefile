.PHONY: help setup test-all test-unit test-integration test-performance test-e2e \
        build deploy clean docker-up docker-down

help:
	@echo "SearchPilot - 사용 가능한 명령어:"
	@echo "  make setup              - 개발 환경 초기 설정"
	@echo "  make test-all           - 모든 테스트 실행 (1,000건)"
	@echo "  make test-unit          - 단위 테스트 실행 (300건)"
	@echo "  make test-integration   - 통합 테스트 실행 (400건)"
	@echo "  make test-performance   - 성능 테스트 실행 (200건)"
	@echo "  make test-e2e           - E2E 테스트 실행 (100건)"
	@echo "  make docker-up          - Docker Compose로 전체 스택 실행"
	@echo "  make docker-down        - Docker Compose 종료"
	@echo "  make build              - Docker 이미지 빌드"
	@echo "  make generate-data      - 테스트 데이터 생성 (100,000건)"
	@echo "  make clean              - 임시 파일 정리"

setup:
	@echo "🚀 개발 환경 설정 중..."
	cd backend && python -m venv venv && . venv/bin/activate && pip install -r requirements.txt
	cd frontend && npm install
	@echo "✅ 설정 완료!"

test-all:
	@echo "🧪 전체 테스트 실행 중 (1,000건)..."
	@./scripts/run_all_tests.sh
	@echo "✅ 모든 테스트 완료!"

test-unit:
	@echo "🧪 단위 테스트 실행 중 (300건)..."
	cd backend && pytest tests/unit -n 16 -v --tb=short

test-integration:
	@echo "🧪 통합 테스트 실행 중 (400건)..."
	cd backend && pytest tests/integration -n 8 -v --tb=short

test-performance:
	@echo "🧪 성능 테스트 실행 중 (200건)..."
	k6 run backend/tests/performance/load_test.js

test-e2e:
	@echo "🧪 E2E 테스트 실행 중 (100건)..."
	cd frontend && npm run test:e2e

docker-up:
	@echo "🐳 Docker Compose 실행 중..."
	docker-compose up -d
	@echo "✅ 서비스 시작됨!"
	@echo "   Backend:  http://localhost:8000"
	@echo "   Frontend: http://localhost:3000"
	@echo "   Prometheus: http://localhost:9090"
	@echo "   Grafana: http://localhost:3001"

docker-down:
	@echo "🛑 Docker Compose 종료 중..."
	docker-compose down

build:
	@echo "🔨 Docker 이미지 빌드 중..."
	docker-compose build

generate-data:
	@echo "📊 테스트 데이터 생성 중 (100,000건)..."
	python scripts/generate_test_data.py
	@echo "✅ 데이터 생성 완료!"

clean:
	@echo "🧹 임시 파일 정리 중..."
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name "node_modules" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	@echo "✅ 정리 완료!"

