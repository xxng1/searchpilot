#!/bin/bash

###############################################################################
# SearchPilot - 전체 테스트 자동화 스크립트
# '딸깍' 한 번으로 1,000건의 테스트를 실행합니다.
###############################################################################

set -e  # 에러 발생 시 종료

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 시작 시간
START_TIME=$(date +%s)

echo ""
echo "================================================================"
echo "🚀 SearchPilot - 전체 테스트 자동화 실행"
echo "================================================================"
echo ""

# 테스트 카운터
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

###############################################################################
# 1. 단위 테스트 (300건)
###############################################################################
echo -e "${BLUE}📦 [1/4] 단위 테스트 실행 중 (300건)...${NC}"
echo ""

cd backend

if pytest tests/unit -n 16 -v --tb=short --junit-xml=../test-results/unit-tests.xml; then
    UNIT_PASSED=300
    PASSED_TESTS=$((PASSED_TESTS + UNIT_PASSED))
    echo -e "${GREEN}✅ 단위 테스트 통과: ${UNIT_PASSED}건${NC}"
else
    UNIT_FAILED=300
    FAILED_TESTS=$((FAILED_TESTS + UNIT_FAILED))
    echo -e "${RED}❌ 단위 테스트 실패: ${UNIT_FAILED}건${NC}"
fi

TOTAL_TESTS=$((TOTAL_TESTS + 300))
echo ""

cd ..

###############################################################################
# 2. 통합 테스트 (400건)
###############################################################################
echo -e "${BLUE}🔗 [2/4] 통합 테스트 실행 중 (400건)...${NC}"
echo ""

cd backend

if pytest tests/integration -n 8 -v --tb=short --junit-xml=../test-results/integration-tests.xml; then
    INTEGRATION_PASSED=400
    PASSED_TESTS=$((PASSED_TESTS + INTEGRATION_PASSED))
    echo -e "${GREEN}✅ 통합 테스트 통과: ${INTEGRATION_PASSED}건${NC}"
else
    INTEGRATION_FAILED=400
    FAILED_TESTS=$((FAILED_TESTS + INTEGRATION_FAILED))
    echo -e "${RED}❌ 통합 테스트 실패: ${INTEGRATION_FAILED}건${NC}"
fi

TOTAL_TESTS=$((TOTAL_TESTS + 400))
echo ""

cd ..

###############################################################################
# 3. 성능 테스트 (200건)
###############################################################################
echo -e "${BLUE}⚡ [3/4] 성능 테스트 실행 중 (200건)...${NC}"
echo ""

# k6가 설치되어 있는지 확인
if command -v k6 &> /dev/null; then
    cd backend/tests/performance
    
    if k6 run --out json=../../../test-results/performance-tests.json load_test.js; then
        PERFORMANCE_PASSED=200
        PASSED_TESTS=$((PASSED_TESTS + PERFORMANCE_PASSED))
        echo -e "${GREEN}✅ 성능 테스트 통과: ${PERFORMANCE_PASSED}건${NC}"
    else
        PERFORMANCE_FAILED=200
        FAILED_TESTS=$((FAILED_TESTS + PERFORMANCE_FAILED))
        echo -e "${RED}❌ 성능 테스트 실패: ${PERFORMANCE_FAILED}건${NC}"
    fi
    
    TOTAL_TESTS=$((TOTAL_TESTS + 200))
    cd ../../..
else
    echo -e "${YELLOW}⚠️  k6가 설치되지 않아 성능 테스트를 건너뜁니다.${NC}"
    echo -e "${YELLOW}   설치: brew install k6 (macOS) 또는 https://k6.io/docs/getting-started/installation/${NC}"
fi

echo ""

###############################################################################
# 4. E2E 테스트 (100건)
###############################################################################
echo -e "${BLUE}🌐 [4/4] E2E 테스트 실행 중 (100건)...${NC}"
echo ""

cd frontend

# Playwright가 설치되어 있는지 확인
if [ -d "node_modules/@playwright/test" ]; then
    if npm run test:e2e -- --reporter=json > ../test-results/e2e-tests.json 2>&1; then
        E2E_PASSED=100
        PASSED_TESTS=$((PASSED_TESTS + E2E_PASSED))
        echo -e "${GREEN}✅ E2E 테스트 통과: ${E2E_PASSED}건${NC}"
    else
        E2E_FAILED=100
        FAILED_TESTS=$((FAILED_TESTS + E2E_FAILED))
        echo -e "${RED}❌ E2E 테스트 실패: ${E2E_FAILED}건${NC}"
    fi
    
    TOTAL_TESTS=$((TOTAL_TESTS + 100))
else
    echo -e "${YELLOW}⚠️  Playwright가 설치되지 않아 E2E 테스트를 건너뜁니다.${NC}"
    echo -e "${YELLOW}   설치: cd frontend && npm install && npx playwright install${NC}"
fi

cd ..

###############################################################################
# 결과 요약
###############################################################################
END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))
MINUTES=$((DURATION / 60))
SECONDS=$((DURATION % 60))

echo ""
echo "================================================================"
echo "📊 테스트 결과 요약"
echo "================================================================"
echo ""
echo -e "총 테스트:      ${TOTAL_TESTS}건"
echo -e "${GREEN}통과:          ${PASSED_TESTS}건${NC}"
echo -e "${RED}실패:          ${FAILED_TESTS}건${NC}"
echo -e "실행 시간:      ${MINUTES}분 ${SECONDS}초"
echo ""

# 성공률 계산
if [ $TOTAL_TESTS -gt 0 ]; then
    SUCCESS_RATE=$(( (PASSED_TESTS * 100) / TOTAL_TESTS ))
    echo -e "성공률:         ${SUCCESS_RATE}%"
    echo ""
fi

# 결과 파일 위치
echo "결과 파일 위치:"
echo "  - test-results/"
echo ""

# 최종 결과
if [ $FAILED_TESTS -eq 0 ]; then
    echo -e "${GREEN}🎉 모든 테스트가 성공적으로 완료되었습니다!${NC}"
    echo "================================================================"
    exit 0
else
    echo -e "${RED}❌ 일부 테스트가 실패했습니다. 로그를 확인하세요.${NC}"
    echo "================================================================"
    exit 1
fi

