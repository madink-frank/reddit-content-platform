import { test, expect } from '@playwright/test';

test.describe('Authentication Flow', () => {
  test.beforeEach(async ({ page }) => {
    // Mock the Reddit OAuth endpoint
    await page.route('**/auth/reddit', async route => {
      await route.fulfill({
        status: 302,
        headers: {
          'Location': 'http://localhost:5173/auth/callback?code=test_code&state=test_state'
        }
      });
    });

    // Mock the token exchange endpoint
    await page.route('**/api/v1/auth/callback', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          user: {
            id: 1,
            name: 'Test User',
            email: 'test@example.com',
            oauth_provider: 'reddit'
          },
          tokens: {
            access_token: 'test_access_token',
            refresh_token: 'test_refresh_token',
            token_type: 'bearer',
            expires_in: 3600
          }
        })
      });
    });
  });

  test('should display login page when not authenticated', async ({ page }) => {
    await page.goto('/');
    
    await expect(page.getByText('Sign in with Reddit')).toBeVisible();
    await expect(page.getByText('Reddit Content Platform')).toBeVisible();
  });

  test('should redirect to dashboard after successful login', async ({ page }) => {
    await page.goto('/');
    
    // Click the login button
    await page.getByText('Sign in with Reddit').click();
    
    // Should redirect to dashboard
    await expect(page).toHaveURL('/dashboard');
    await expect(page.getByText('Welcome, Test User')).toBeVisible();
  });

  test('should handle OAuth callback correctly', async ({ page }) => {
    // Navigate directly to callback URL
    await page.goto('/auth/callback?code=test_code&state=test_state');
    
    // Should process the callback and redirect to dashboard
    await expect(page).toHaveURL('/dashboard');
    await expect(page.getByText('Test User')).toBeVisible();
  });

  test('should show error for invalid OAuth state', async ({ page }) => {
    await page.route('**/api/v1/auth/callback', async route => {
      await route.fulfill({
        status: 400,
        contentType: 'application/json',
        body: JSON.stringify({
          message: 'Invalid OAuth state parameter'
        })
      });
    });

    await page.goto('/auth/callback?code=test_code&state=invalid_state');
    
    await expect(page.getByText('Invalid OAuth state parameter')).toBeVisible();
  });

  test('should logout successfully', async ({ page }) => {
    // Set up authenticated state
    await page.addInitScript(() => {
      localStorage.setItem('test_access_token', 'test_token');
      localStorage.setItem('test_user', JSON.stringify({
        id: 1,
        name: 'Test User',
        email: 'test@example.com'
      }));
    });

    await page.goto('/dashboard');
    
    // Click logout button
    await page.getByRole('button', { name: /logout/i }).click();
    
    // Should redirect to login page
    await expect(page).toHaveURL('/');
    await expect(page.getByText('Sign in with Reddit')).toBeVisible();
  });

  test('should persist authentication across page reloads', async ({ page }) => {
    // Set up authenticated state
    await page.addInitScript(() => {
      localStorage.setItem('test_access_token', 'test_token');
      localStorage.setItem('test_user', JSON.stringify({
        id: 1,
        name: 'Test User',
        email: 'test@example.com'
      }));
    });

    await page.goto('/dashboard');
    await expect(page.getByText('Test User')).toBeVisible();
    
    // Reload the page
    await page.reload();
    
    // Should still be authenticated
    await expect(page.getByText('Test User')).toBeVisible();
  });

  test('should handle token refresh', async ({ page }) => {
    // Mock refresh token endpoint
    await page.route('**/api/v1/auth/refresh', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          access_token: 'new_access_token',
          refresh_token: 'new_refresh_token',
          token_type: 'bearer',
          expires_in: 3600
        })
      });
    });

    // Set up expired token
    await page.addInitScript(() => {
      localStorage.setItem('test_access_token', 'expired_token');
      localStorage.setItem('test_refresh_token', 'refresh_token');
      localStorage.setItem('test_expires_at', (Date.now() - 1000).toString());
      localStorage.setItem('test_user', JSON.stringify({
        id: 1,
        name: 'Test User',
        email: 'test@example.com'
      }));
    });

    await page.goto('/dashboard');
    
    // Should automatically refresh token and stay authenticated
    await expect(page.getByText('Test User')).toBeVisible();
  });
});