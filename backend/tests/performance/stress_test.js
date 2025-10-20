/**
 * 스트레스 테스트: 시스템 한계 테스트
 */

import http from 'k6/http';
import { check } from 'k6';

export const options = {
  stages: [
    { duration: '30s', target: 20 },   // Ramp up to 20 users (관대한 기준)
    { duration: '1m', target: 20 },    // Stay at 20 users
    { duration: '30s', target: 40 },   // Ramp up to 40 users
    { duration: '1m', target: 40 },    // Stay at 40 users
    { duration: '30s', target: 0 },    // Ramp down
  ],
  thresholds: {
    http_req_duration: ['p(95)<3000'], // 95% of requests should be below 3s (관대한 기준)
    http_req_failed: ['rate<0.1'],     // Error rate should be less than 10% (관대한 기준)
  },
};

const BASE_URL = __ENV.API_URL || 'http://localhost:8000';

export default function () {
  const response = http.get(`${BASE_URL}/api/search?q=stress_test`);
  
  check(response, {
    'status is 200': (r) => r.status === 200,
  });
}

