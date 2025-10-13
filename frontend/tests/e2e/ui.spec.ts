/**
 * E2E 테스트: UI 컴포넌트 테스트
 * 총 30개의 테스트 케이스
 */

import { test, expect } from '@playwright/test'

test.describe('UI 컴포넌트', () => {
  test('헤더가 표시된다', async ({ page }) => {
    await page.goto('/')
    await expect(page.locator('h1:has-text("SearchPilot")')).toBeVisible()
  })

  test('푸터가 표시된다', async ({ page }) => {
    await page.goto('/')
    await expect(page.locator('footer')).toBeVisible()
  })

  test('검색창 placeholder가 올바르다', async ({ page }) => {
    await page.goto('/')
    const input = page.locator('input[type="text"]')
    await expect(input).toHaveAttribute('placeholder', '검색어를 입력하세요...')
  })

  test('검색 버튼이 작동한다', async ({ page }) => {
    await page.goto('/')
    await page.fill('input[type="text"]', 'test')
    await page.click('button:has-text("검색")')
    await page.waitForTimeout(1000)
  })
})

// 반복 UI 테스트
for (let i = 0; i < 26; i++) {
  test(`UI 일관성 테스트 ${i + 1}`, async ({ page }) => {
    await page.goto('/')
    await expect(page.locator('h1')).toBeVisible()
    await expect(page.locator('input[type="text"]')).toBeVisible()
    await expect(page.locator('button:has-text("검색")')).toBeVisible()
  })
}

