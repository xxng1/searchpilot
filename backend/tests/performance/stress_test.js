/**
 * 스트레스 테스트: 시스템 한계 테스트
 */

import http from 'k6/http';
import { check } from 'k6';

export const options = {
  stages: [
    { duration: '2m', target: 200 },  // Ramp up to 200 users
    { duration: '5m', target: 200 },  // Stay at 200 users
    { duration: '2m', target: 400 },  // Ramp up to 400 users
    { duration: '5m', target: 400 },  // Stay at 400 users
    { duration: '2m', target: 0 },    // Ramp down
  ],
};

const BASE_URL = __ENV.API_URL || 'http://localhost:8000';

export default function () {
  const response = http.get(`${BASE_URL}/api/search?q=stress_test`);
  
  check(response, {
    'status is 200': (r) => r.status === 200,
  });
}

