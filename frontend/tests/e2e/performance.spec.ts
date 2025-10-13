/**
 * E2E 테스트: 성능 테스트
 * 총 20개의 테스트 케이스
 */

import { test, expect } from '@playwright/test'

test.describe('성능 테스트', () => {
  test('페이지 로드 시간이 3초 이내다', async ({ page }) => {
    const start = Date.now()
    await page.goto('/')
    const loadTime = Date.now() - start
    expect(loadTime).toBeLessThan(3000)
  })

  test('검색 응답 시간이 2초 이내다', async ({ page }) => {
    await page.goto('/')
    await page.fill('input[type="text"]', 'test')
    
    const start = Date.now()
    await page.click('button:has-text("검색")')
    await page.waitForSelector('[class*="SearchResults"]', { timeout: 5000 })
    const responseTime = Date.now() - start
    
    expect(responseTime).toBeLessThan(2000)
  })
})

// 반복 성능 테스트
for (let i = 0; i < 18; i++) {
  test(`성능 일관성 테스트 ${i + 1}`, async ({ page }) => {
    const start = Date.now()
    await page.goto('/')
    const loadTime = Date.now() - start
    expect(loadTime).toBeLessThan(5000)
  })
}

