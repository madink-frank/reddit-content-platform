import { test, expect } from '@playwright/test';

test.describe('Keywords Management', () => {
  test.beforeEach(async ({ page }) => {
    // Set up authenticated state
    await page.addInitScript(() => {
      localStorage.setItem('test_access_token', 'test_token');
      localStorage.setItem('test_user', JSON.stringify({
        id: 1,
        name: 'Test User',
        email: 'test@example.com'
      }));
    });

    // Mock keywords API
    await page.route('**/api/v1/keywords', async route => {
      if (route.request().method() === 'GET') {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify([
            {
              id: 1,
              keyword: 'react',
              is_active: true,
              created_at: '2024-01-01T00:00:00Z'
            },
            {
              id: 2,
              keyword: 'javascript',
              is_active: false,
              created_at: '2024-01-02T00:00:00Z'
            }
          ])
        });
      } else if (route.request().method() === 'POST') {
        const body = await route.request().postDataJSON();
        await route.fulfill({
          status: 201,
          contentType: 'application/json',
          body: JSON.stringify({
            id: 3,
            keyword: body.keyword,
            is_active: true,
            created_at: new Date().toISOString()
          })
        });
      }
    });

    await page.goto('/keywords');
  });

  test('should display keywords list', async ({ page }) => {
    await expect(page.getByText('react')).toBeVisible();
    await expect(page.getByText('javascript')).toBeVisible();
    await expect(page.getByText('Active')).toBeVisible();
    await expect(page.getByText('Inactive')).toBeVisible();
  });

  test('should add new keyword', async ({ page }) => {
    // Click add keyword button
    await page.getByText('Add Keyword').click();
    
    // Fill in the form
    await page.getByLabel(/keyword/i).fill('typescript');
    
    // Submit the form
    await page.getByText('Create').click();
    
    // Should show success message
    await expect(page.getByText('Keyword created successfully')).toBeVisible();
  });

  test('should validate keyword input', async ({ page }) => {
    await page.getByText('Add Keyword').click();
    
    // Try to submit empty form
    await page.getByText('Create').click();
    
    // Should show validation error
    await expect(page.getByText('Keyword is required')).toBeVisible();
    
    // Try invalid characters
    await page.getByLabel(/keyword/i).fill('test@#$');
    
    await expect(page.getByText(/Only letters, numbers, spaces, hyphens, and underscores are allowed/)).toBeVisible();
  });

  test('should edit existing keyword', async ({ page }) => {
    // Mock update endpoint
    await page.route('**/api/v1/keywords/1', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          id: 1,
          keyword: 'react-hooks',
          is_active: true,
          created_at: '2024-01-01T00:00:00Z'
        })
      });
    });

    // Click edit button for first keyword
    await page.getByTitle('Edit keyword').first().click();
    
    // Update the keyword
    await page.getByDisplayValue('react').fill('react-hooks');
    
    // Submit the form
    await page.getByText('Update').click();
    
    // Should show success message
    await expect(page.getByText('Keyword updated successfully')).toBeVisible();
  });

  test('should delete keyword', async ({ page }) => {
    // Mock delete endpoint
    await page.route('**/api/v1/keywords/1', async route => {
      if (route.request().method() === 'DELETE') {
        await route.fulfill({ status: 204 });
      }
    });

    // Click delete button
    await page.getByTitle('Delete keyword').first().click();
    
    // Confirm deletion
    await page.getByText('Delete').click();
    
    // Should show success message
    await expect(page.getByText('Keyword deleted successfully')).toBeVisible();
  });

  test('should toggle keyword status', async ({ page }) => {
    // Mock toggle endpoint
    await page.route('**/api/v1/keywords/1/toggle', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          id: 1,
          keyword: 'react',
          is_active: false,
          created_at: '2024-01-01T00:00:00Z'
        })
      });
    });

    // Click toggle switch
    await page.getByRole('switch').first().click();
    
    // Should show updated status
    await expect(page.getByText('Keyword status updated')).toBeVisible();
  });

  test('should filter keywords', async ({ page }) => {
    // Test search filter
    await page.getByPlaceholder('Search keywords...').fill('react');
    
    await expect(page.getByText('react')).toBeVisible();
    await expect(page.getByText('javascript')).not.toBeVisible();
    
    // Clear search
    await page.getByPlaceholder('Search keywords...').clear();
    
    // Test status filter
    await page.getByText('Active Only').click();
    
    await expect(page.getByText('react')).toBeVisible();
    await expect(page.getByText('javascript')).not.toBeVisible();
  });

  test('should handle empty state', async ({ page }) => {
    // Mock empty response
    await page.route('**/api/v1/keywords', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify([])
      });
    });

    await page.reload();
    
    await expect(page.getByText('No keywords yet')).toBeVisible();
    await expect(page.getByText('Get started by adding your first keyword.')).toBeVisible();
  });

  test('should handle API errors', async ({ page }) => {
    // Mock error response
    await page.route('**/api/v1/keywords', async route => {
      if (route.request().method() === 'POST') {
        await route.fulfill({
          status: 500,
          contentType: 'application/json',
          body: JSON.stringify({
            message: 'Internal server error'
          })
        });
      }
    });

    await page.getByText('Add Keyword').click();
    await page.getByLabel(/keyword/i).fill('test');
    await page.getByText('Create').click();
    
    await expect(page.getByText('Failed to create keyword')).toBeVisible();
  });

  test('should be responsive on mobile', async ({ page }) => {
    // Set mobile viewport
    await page.setViewportSize({ width: 375, height: 667 });
    
    // Should show mobile-friendly layout
    await expect(page.getByText('Keywords')).toBeVisible();
    await expect(page.getByText('Add Keyword')).toBeVisible();
    
    // Keywords should be displayed in mobile format
    await expect(page.getByText('react')).toBeVisible();
  });
});