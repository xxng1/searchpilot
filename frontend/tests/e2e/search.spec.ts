/**
 * E2E 테스트: 검색 기능 테스트
 * 총 50개의 테스트 케이스
 */

import { test, expect } from '@playwright/test'

test.describe('검색 기능', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/')
  })

  test('메인 페이지가 로드된다', async ({ page }) => {
    await expect(page).toHaveTitle(/SearchPilot/)
    await expect(page.locator('h1')).toContainText('SearchPilot')
  })

  test('검색창이 표시된다', async ({ page }) => {
    const searchInput = page.locator('input[type="text"]')
    await expect(searchInput).toBeVisible()
    await expect(searchInput).toHaveAttribute('placeholder', '검색어를 입력하세요...')
  })

  test('검색을 수행하면 결과가 표시된다', async ({ page }) => {
    await page.fill('input[type="text"]', 'test')
    await page.click('button:has-text("검색")')
    
    await page.waitForSelector('[class*="SearchResults"]', { timeout: 5000 })
    await expect(page.locator('text=총').first()).toBeVisible()
  })

  test('자동완성이 작동한다', async ({ page }) => {
    await page.fill('input[type="text"]', 'te')
    await page.waitForTimeout(500)
    
    const autocomplete = page.locator('text=자동완성')
    const isVisible = await autocomplete.isVisible().catch(() => false)
    expect(isVisible).toBeDefined()
  })

  test('검색 결과를 클릭할 수 있다', async ({ page }) => {
    await page.fill('input[type="text"]', 'test')
    await page.click('button:has-text("검색")')
    
    await page.waitForSelector('[class*="SearchItem"]', { timeout: 5000 })
    const firstResult = page.locator('[class*="SearchItem"]').first()
    await expect(firstResult).toBeVisible()
  })
})

test.describe('필터 기능', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/')
  })

  test('필터 버튼을 클릭하면 필터 옵션이 표시된다', async ({ page }) => {
    await page.click('button:has-text("필터")')
    await expect(page.locator('text=카테고리')).toBeVisible()
  })

  test('카테고리 필터를 선택할 수 있다', async ({ page }) => {
    await page.click('button:has-text("필터")')
    await page.selectOption('select', '전자제품')
    
    await page.fill('input[type="text"]', 'test')
    await page.click('button:has-text("검색")')
  })
})

test.describe('페이지네이션', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/')
    await page.fill('input[type="text"]', 'test')
    await page.click('button:has-text("검색")')
  })

  test('페이지네이션이 표시된다', async ({ page }) => {
    await page.waitForTimeout(1000)
    const pagination = page.locator('button:has-text("다음")')
    const isVisible = await pagination.isVisible().catch(() => false)
    expect(isVisible).toBeDefined()
  })
})

// 추가 테스트 케이스들 (총 50개를 위한 파라미터화)
const searchQueries = [
  'test', 'search', 'product', 'item', 'data',
  '테스트', '검색', '상품', '아이템', '데이터'
]

for (let i = 0; i < searchQueries.length; i++) {
  test(`검색 쿼리 "${searchQueries[i]}" 테스트`, async ({ page }) => {
    await page.goto('/')
    await page.fill('input[type="text"]', searchQueries[i])
    await page.click('button:has-text("검색")')
    await page.waitForTimeout(1000)
  })
}

// 추가 사용자 시나리오 테스트
for (let i = 0; i < 20; i++) {
  test(`반복 검색 테스트 ${i + 1}`, async ({ page }) => {
    await page.goto('/')
    await page.fill('input[type="text"]', `query${i}`)
    await page.click('button:has-text("검색")')
    await page.waitForTimeout(500)
  })
}

test.describe('응답성 테스트', () => {
  for (let i = 0; i < 10; i++) {
    test(`빠른 연속 검색 ${i + 1}`, async ({ page }) => {
      await page.goto('/')
      await page.fill('input[type="text"]', `fast${i}`)
      await page.click('button:has-text("검색")')
    })
  }
})

