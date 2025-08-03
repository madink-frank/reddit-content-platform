#!/usr/bin/env node

/**
 * Performance monitoring script for frontend applications
 * Measures Core Web Vitals and other performance metrics
 */

const puppeteer = require('puppeteer');
const fs = require('fs').promises;
const path = require('path');

class PerformanceMonitor {
  constructor(options = {}) {
    this.options = {
      headless: true,
      timeout: 30000,
      viewport: { width: 1920, height: 1080 },
      ...options
    };
    this.results = [];
  }

  async measurePage(url, name = 'page') {
    console.log(`🔍 Measuring performance for: ${url}`);
    
    const browser = await puppeteer.launch({
      headless: this.options.headless,
      args: ['--no-sandbox', '--disable-setuid-sandbox']
    });

    try {
      const page = await browser.newPage();
      await page.setViewport(this.options.viewport);

      // Enable performance metrics collection
      await page.evaluateOnNewDocument(() => {
        window.performanceMetrics = {
          navigationStart: 0,
          loadComplete: 0,
          firstPaint: 0,
          firstContentfulPaint: 0,
          largestContentfulPaint: 0,
          firstInputDelay: 0,
          cumulativeLayoutShift: 0,
          totalBlockingTime: 0
        };

        // Measure Core Web Vitals
        new PerformanceObserver((list) => {
          for (const entry of list.getEntries()) {
            if (entry.entryType === 'paint') {
              if (entry.name === 'first-paint') {
                window.performanceMetrics.firstPaint = entry.startTime;
              } else if (entry.name === 'first-contentful-paint') {
                window.performanceMetrics.firstContentfulPaint = entry.startTime;
              }
            } else if (entry.entryType === 'largest-contentful-paint') {
              window.performanceMetrics.largestContentfulPaint = entry.startTime;
            } else if (entry.entryType === 'first-input') {
              window.performanceMetrics.firstInputDelay = entry.processingStart - entry.startTime;
            } else if (entry.entryType === 'layout-shift') {
              if (!entry.hadRecentInput) {
                window.performanceMetrics.cumulativeLayoutShift += entry.value;
              }
            }
          }
        }).observe({ entryTypes: ['paint', 'largest-contentful-paint', 'first-input', 'layout-shift'] });

        // Measure Total Blocking Time
        new PerformanceObserver((list) => {
          for (const entry of list.getEntries()) {
            if (entry.duration > 50) {
              window.performanceMetrics.totalBlockingTime += entry.duration - 50;
            }
          }
        }).observe({ entryTypes: ['longtask'] });
      });

      const startTime = Date.now();
      
      // Navigate to page and wait for load
      await page.goto(url, { 
        waitUntil: 'networkidle0',
        timeout: this.options.timeout 
      });

      // Wait a bit more for any lazy-loaded content
      await page.waitForTimeout(2000);

      const endTime = Date.now();
      const loadTime = endTime - startTime;

      // Get performance metrics
      const metrics = await page.evaluate(() => {
        const navigation = performance.getEntriesByType('navigation')[0];
        const resources = performance.getEntriesByType('resource');
        
        return {
          // Navigation timing
          navigationStart: navigation.navigationStart,
          domContentLoaded: navigation.domContentLoadedEventEnd - navigation.navigationStart,
          loadComplete: navigation.loadEventEnd - navigation.navigationStart,
          
          // Core Web Vitals
          firstPaint: window.performanceMetrics.firstPaint,
          firstContentfulPaint: window.performanceMetrics.firstContentfulPaint,
          largestContentfulPaint: window.performanceMetrics.largestContentfulPaint,
          firstInputDelay: window.performanceMetrics.firstInputDelay,
          cumulativeLayoutShift: window.performanceMetrics.cumulativeLayoutShift,
          totalBlockingTime: window.performanceMetrics.totalBlockingTime,
          
          // Resource metrics
          totalResources: resources.length,
          totalResourceSize: resources.reduce((sum, resource) => sum + (resource.transferSize || 0), 0),
          jsResources: resources.filter(r => r.name.includes('.js')).length,
          cssResources: resources.filter(r => r.name.includes('.css')).length,
          imageResources: resources.filter(r => /\.(png|jpg|jpeg|gif|svg|webp)/.test(r.name)).length,
          
          // Memory usage (if available)
          memoryUsage: performance.memory ? {
            usedJSHeapSize: performance.memory.usedJSHeapSize,
            totalJSHeapSize: performance.memory.totalJSHeapSize,
            jsHeapSizeLimit: performance.memory.jsHeapSizeLimit
          } : null
        };
      });

      // Get Lighthouse-style scores
      const scores = this.calculateScores(metrics);

      const result = {
        name,
        url,
        timestamp: new Date().toISOString(),
        loadTime,
        metrics,
        scores,
        recommendations: this.generateRecommendations(metrics, scores)
      };

      this.results.push(result);
      
      console.log(`✅ Performance measurement complete for ${name}`);
      console.log(`   Load Time: ${loadTime}ms`);
      console.log(`   FCP: ${metrics.firstContentfulPaint.toFixed(1)}ms`);
      console.log(`   LCP: ${metrics.largestContentfulPaint.toFixed(1)}ms`);
      console.log(`   CLS: ${metrics.cumulativeLayoutShift.toFixed(3)}`);
      console.log(`   Performance Score: ${scores.performance}/100`);

      return result;

    } finally {
      await browser.close();
    }
  }

  calculateScores(metrics) {
    // Lighthouse-inspired scoring
    const scores = {
      performance: 0,
      accessibility: 0, // Would need additional checks
      bestPractices: 0, // Would need additional checks
      seo: 0 // Would need additional checks
    };

    // Performance score calculation (simplified)
    let performanceScore = 100;

    // First Contentful Paint (10% weight)
    if (metrics.firstContentfulPaint > 3000) performanceScore -= 20;
    else if (metrics.firstContentfulPaint > 1800) performanceScore -= 10;

    // Largest Contentful Paint (25% weight)
    if (metrics.largestContentfulPaint > 4000) performanceScore -= 30;
    else if (metrics.largestContentfulPaint > 2500) performanceScore -= 15;

    // Total Blocking Time (30% weight)
    if (metrics.totalBlockingTime > 600) performanceScore -= 35;
    else if (metrics.totalBlockingTime > 300) performanceScore -= 20;

    // Cumulative Layout Shift (25% weight)
    if (metrics.cumulativeLayoutShift > 0.25) performanceScore -= 25;
    else if (metrics.cumulativeLayoutShift > 0.1) performanceScore -= 10;

    // Speed Index approximation (10% weight)
    if (metrics.domContentLoaded > 3000) performanceScore -= 10;
    else if (metrics.domContentLoaded > 1500) performanceScore -= 5;

    scores.performance = Math.max(0, Math.min(100, performanceScore));

    return scores;
  }

  generateRecommendations(metrics, scores) {
    const recommendations = [];

    if (metrics.firstContentfulPaint > 1800) {
      recommendations.push({
        type: 'performance',
        priority: 'high',
        message: 'First Contentful Paint is slow. Consider optimizing critical rendering path.',
        metric: 'FCP',
        value: metrics.firstContentfulPaint,
        threshold: 1800
      });
    }

    if (metrics.largestContentfulPaint > 2500) {
      recommendations.push({
        type: 'performance',
        priority: 'high',
        message: 'Largest Contentful Paint is slow. Optimize images and critical resources.',
        metric: 'LCP',
        value: metrics.largestContentfulPaint,
        threshold: 2500
      });
    }

    if (metrics.totalBlockingTime > 300) {
      recommendations.push({
        type: 'performance',
        priority: 'medium',
        message: 'Total Blocking Time is high. Consider code splitting and reducing JavaScript execution time.',
        metric: 'TBT',
        value: metrics.totalBlockingTime,
        threshold: 300
      });
    }

    if (metrics.cumulativeLayoutShift > 0.1) {
      recommendations.push({
        type: 'performance',
        priority: 'medium',
        message: 'Cumulative Layout Shift is high. Ensure images and ads have dimensions.',
        metric: 'CLS',
        value: metrics.cumulativeLayoutShift,
        threshold: 0.1
      });
    }

    if (metrics.totalResourceSize > 2 * 1024 * 1024) { // 2MB
      recommendations.push({
        type: 'optimization',
        priority: 'medium',
        message: 'Total resource size is large. Consider compression and code splitting.',
        metric: 'Resource Size',
        value: metrics.totalResourceSize,
        threshold: 2 * 1024 * 1024
      });
    }

    return recommendations;
  }

  async generateReport(outputPath = './performance-report.json') {
    const report = {
      generated: new Date().toISOString(),
      summary: {
        totalPages: this.results.length,
        averageLoadTime: this.results.reduce((sum, r) => sum + r.loadTime, 0) / this.results.length,
        averagePerformanceScore: this.results.reduce((sum, r) => sum + r.scores.performance, 0) / this.results.length,
        totalRecommendations: this.results.reduce((sum, r) => sum + r.recommendations.length, 0)
      },
      results: this.results,
      recommendations: this.results.flatMap(r => r.recommendations)
    };

    await fs.writeFile(outputPath, JSON.stringify(report, null, 2));
    console.log(`📊 Performance report saved to: ${outputPath}`);

    // Generate HTML report
    const htmlReport = this.generateHTMLReport(report);
    const htmlPath = outputPath.replace('.json', '.html');
    await fs.writeFile(htmlPath, htmlReport);
    console.log(`📊 HTML report saved to: ${htmlPath}`);

    return report;
  }

  generateHTMLReport(report) {
    return `
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Performance Report</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .header { text-align: center; margin-bottom: 30px; }
        .summary { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 30px; }
        .metric { background: #f8f9fa; padding: 15px; border-radius: 6px; text-align: center; }
        .metric-value { font-size: 24px; font-weight: bold; color: #007bff; }
        .metric-label { font-size: 14px; color: #666; margin-top: 5px; }
        .results { margin-bottom: 30px; }
        .result { border: 1px solid #ddd; border-radius: 6px; margin-bottom: 20px; overflow: hidden; }
        .result-header { background: #f8f9fa; padding: 15px; font-weight: bold; }
        .result-body { padding: 15px; }
        .metrics-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 10px; margin-bottom: 15px; }
        .metric-item { text-align: center; padding: 10px; background: #f8f9fa; border-radius: 4px; }
        .recommendations { margin-top: 15px; }
        .recommendation { padding: 10px; margin-bottom: 10px; border-left: 4px solid #ffc107; background: #fff3cd; border-radius: 4px; }
        .recommendation.high { border-left-color: #dc3545; background: #f8d7da; }
        .recommendation.medium { border-left-color: #ffc107; background: #fff3cd; }
        .recommendation.low { border-left-color: #28a745; background: #d4edda; }
        .score { display: inline-block; padding: 4px 8px; border-radius: 4px; color: white; font-weight: bold; }
        .score.good { background: #28a745; }
        .score.average { background: #ffc107; }
        .score.poor { background: #dc3545; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Performance Report</h1>
            <p>Generated on ${new Date(report.generated).toLocaleString()}</p>
        </div>
        
        <div class="summary">
            <div class="metric">
                <div class="metric-value">${report.summary.totalPages}</div>
                <div class="metric-label">Pages Tested</div>
            </div>
            <div class="metric">
                <div class="metric-value">${Math.round(report.summary.averageLoadTime)}ms</div>
                <div class="metric-label">Avg Load Time</div>
            </div>
            <div class="metric">
                <div class="metric-value">${Math.round(report.summary.averagePerformanceScore)}</div>
                <div class="metric-label">Avg Performance Score</div>
            </div>
            <div class="metric">
                <div class="metric-value">${report.summary.totalRecommendations}</div>
                <div class="metric-label">Total Recommendations</div>
            </div>
        </div>
        
        <div class="results">
            <h2>Page Results</h2>
            ${report.results.map(result => `
                <div class="result">
                    <div class="result-header">
                        ${result.name} - ${result.url}
                        <span class="score ${result.scores.performance >= 90 ? 'good' : result.scores.performance >= 50 ? 'average' : 'poor'}">
                            ${result.scores.performance}/100
                        </span>
                    </div>
                    <div class="result-body">
                        <div class="metrics-grid">
                            <div class="metric-item">
                                <div><strong>${Math.round(result.metrics.firstContentfulPaint)}ms</strong></div>
                                <div>First Contentful Paint</div>
                            </div>
                            <div class="metric-item">
                                <div><strong>${Math.round(result.metrics.largestContentfulPaint)}ms</strong></div>
                                <div>Largest Contentful Paint</div>
                            </div>
                            <div class="metric-item">
                                <div><strong>${result.metrics.cumulativeLayoutShift.toFixed(3)}</strong></div>
                                <div>Cumulative Layout Shift</div>
                            </div>
                            <div class="metric-item">
                                <div><strong>${Math.round(result.metrics.totalBlockingTime)}ms</strong></div>
                                <div>Total Blocking Time</div>
                            </div>
                        </div>
                        
                        ${result.recommendations.length > 0 ? `
                            <div class="recommendations">
                                <h4>Recommendations</h4>
                                ${result.recommendations.map(rec => `
                                    <div class="recommendation ${rec.priority}">
                                        <strong>${rec.metric}:</strong> ${rec.message}
                                    </div>
                                `).join('')}
                            </div>
                        ` : ''}
                    </div>
                </div>
            `).join('')}
        </div>
    </div>
</body>
</html>
    `;
  }
}

// CLI usage
async function main() {
  const args = process.argv.slice(2);
  
  if (args.length === 0) {
    console.log('Usage: node performance-monitor.js <url1> [url2] [url3] ...');
    console.log('Example: node performance-monitor.js https://example.com https://example.com/about');
    process.exit(1);
  }

  const monitor = new PerformanceMonitor();
  
  for (const url of args) {
    try {
      await monitor.measurePage(url, new URL(url).pathname);
    } catch (error) {
      console.error(`❌ Failed to measure ${url}:`, error.message);
    }
  }

  if (monitor.results.length > 0) {
    await monitor.generateReport('./performance-report.json');
    console.log('\n🎉 Performance monitoring complete!');
  } else {
    console.log('❌ No successful measurements to report.');
  }
}

if (require.main === module) {
  main().catch(console.error);
}

module.exports = PerformanceMonitor;