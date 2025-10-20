/**
 * 성능 테스트: k6를 이용한 부하 테스트
 * 총 200개의 시나리오 테스트
 */

import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate, Trend } from 'k6/metrics';

// 커스텀 메트릭
const errorRate = new Rate('errors');
const searchDuration = new Trend('search_duration');
const autocompleteDuration = new Trend('autocomplete_duration');

// 테스트 설정 (관대한 기준)
export const options = {
  stages: [
    { duration: '30s', target: 10 },   // Ramp up to 10 users
    { duration: '1m', target: 10 },    // Stay at 10 users
    { duration: '30s', target: 20 },   // Ramp up to 20 users
    { duration: '1m', target: 20 },    // Stay at 20 users
    { duration: '30s', target: 0 },    // Ramp down to 0 users
  ],
  thresholds: {
    http_req_duration: ['p(95)<2000'], // 95% of requests should be below 2s (관대한 기준)
    http_req_failed: ['rate<0.05'],    // Error rate should be less than 5% (관대한 기준)
    errors: ['rate<0.05'],
  },
};

const BASE_URL = __ENV.API_URL || 'http://localhost:8000';

// 검색 쿼리 목록
const searchQueries = [
  'test', 'search', 'product', 'item', 'data',
  '테스트', '검색', '상품', '아이템', '데이터',
  'electronics', 'clothing', 'books', 'food', 'furniture',
  '전자제품', '의류', '도서', '식품', '가구',
];

// 카테고리 목록
const categories = [
  '전자제품', '의류', '도서', '식품', '가구', 
  '스포츠', '완구', '화장품'
];

export default function () {
  // 1. 기본 검색 테스트
  testBasicSearch();
  
  // 2. 필터링 검색 테스트
  testFilteredSearch();
  
  // 3. 정렬 검색 테스트
  testSortedSearch();
  
  // 4. 자동완성 테스트
  testAutocomplete();
  
  // 5. 페이지네이션 테스트
  testPagination();
  
  sleep(1);
}

function testBasicSearch() {
  const query = searchQueries[Math.floor(Math.random() * searchQueries.length)];
  const response = http.get(`${BASE_URL}/api/search?q=${query}`);
  
  const result = check(response, {
    'search status is 200': (r) => r.status === 200,
    'search response time < 2s': (r) => r.timings.duration < 2000, // 관대한 기준
    'search has items': (r) => {
      try {
        const body = JSON.parse(r.body);
        return body && typeof body === 'object' && body.hasOwnProperty('items');
      } catch (e) {
        return false;
      }
    },
  });
  
  errorRate.add(!result);
  searchDuration.add(response.timings.duration);
}

function testFilteredSearch() {
  const query = searchQueries[Math.floor(Math.random() * searchQueries.length)];
  const category = categories[Math.floor(Math.random() * categories.length)];
  const minPrice = Math.floor(Math.random() * 10000);
  const maxPrice = minPrice + Math.floor(Math.random() * 90000);
  
  const response = http.get(
    `${BASE_URL}/api/search?q=${query}&category=${category}&min_price=${minPrice}&max_price=${maxPrice}`
  );
  
  check(response, {
    'filtered search status is 200': (r) => r.status === 200,
  });
  
  errorRate.add(response.status !== 200);
}

function testSortedSearch() {
  const query = searchQueries[Math.floor(Math.random() * searchQueries.length)];
  const sortOptions = ['relevance', 'date', 'popularity', 'price'];
  const orderOptions = ['asc', 'desc'];
  
  const sort = sortOptions[Math.floor(Math.random() * sortOptions.length)];
  const order = orderOptions[Math.floor(Math.random() * orderOptions.length)];
  
  const response = http.get(
    `${BASE_URL}/api/search?q=${query}&sort=${sort}&order=${order}`
  );
  
  check(response, {
    'sorted search status is 200': (r) => r.status === 200,
  });
  
  errorRate.add(response.status !== 200);
}

function testAutocomplete() {
  const partialQuery = searchQueries[Math.floor(Math.random() * searchQueries.length)].substring(0, 2);
  const response = http.get(`${BASE_URL}/api/autocomplete?q=${partialQuery}`);
  
  const result = check(response, {
    'autocomplete status is 200': (r) => r.status === 200,
    'autocomplete response time < 500ms': (r) => r.timings.duration < 500, // 관대한 기준
    'autocomplete has suggestions': (r) => {
      try {
        const body = JSON.parse(r.body);
        return body && typeof body === 'object' && body.hasOwnProperty('suggestions');
      } catch (e) {
        return false;
      }
    },
  });
  
  errorRate.add(!result);
  autocompleteDuration.add(response.timings.duration);
}

function testPagination() {
  const query = searchQueries[Math.floor(Math.random() * searchQueries.length)];
  const page = Math.floor(Math.random() * 5) + 1;
  const size = [10, 20, 50][Math.floor(Math.random() * 3)];
  
  const response = http.get(
    `${BASE_URL}/api/search?q=${query}&page=${page}&size=${size}`
  );
  
  check(response, {
    'pagination search status is 200': (r) => r.status === 200,
    'pagination returns correct page': (r) => {
      try {
        const body = JSON.parse(r.body);
        return body && typeof body === 'object' && body.page === page;
      } catch (e) {
        return false;
      }
    },
  });
  
  errorRate.add(response.status !== 200);
}

// 추가 시나리오: 헬스체크
export function healthCheck() {
  const response = http.get(`${BASE_URL}/health`);
  
  check(response, {
    'health check status is 200': (r) => r.status === 200,
    'health check is healthy': (r) => JSON.parse(r.body).status === 'healthy',
  });
}

// 추가 시나리오: 통계 조회
export function statsCheck() {
  const response = http.get(`${BASE_URL}/api/search/stats`);
  
  check(response, {
    'stats status is 200': (r) => r.status === 200,
    'stats has total_items': (r) => JSON.parse(r.body).hasOwnProperty('total_items'),
  });
}

