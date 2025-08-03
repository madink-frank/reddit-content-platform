# CI/CD Workflows

This directory contains GitHub Actions workflows for the Reddit Content Platform.

## Workflows Overview

### 1. CI - Test and Lint (`ci.yml`)
**Triggers**: Push to main/develop, Pull Requests
**Purpose**: Continuous Integration - runs tests, linting, and security checks

**Jobs**:
- **Lint**: Code formatting (Black), import sorting (isort), and linting (Flake8)
- **Test**: Full test suite with PostgreSQL and Redis services
- **Security**: Dependency security scanning (Safety, Bandit)
- **Docker**: Build and test Docker images

### 2. CD - Deploy to Railway (`deploy.yml`)
**Triggers**: Push to main, Manual dispatch
**Purpose**: Continuous Deployment to Railway.com

**Jobs**:
- **Test**: Run tests before deployment
- **Deploy**: Deploy to Railway production environment
- **Notify**: Send deployment status notifications

### 3. PR Preview (`pr-preview.yml`)
**Triggers**: Pull Request events
**Purpose**: Deploy preview environments for pull requests

**Jobs**:
- **Test**: Test PR changes
- **Deploy Preview**: Create temporary preview deployment
- **Cleanup**: Remove preview environment when PR is closed

### 4. Security Scanning (`security.yml`)
**Triggers**: Daily schedule, Push to main, Pull Requests, Manual dispatch
**Purpose**: Comprehensive security scanning

**Jobs**:
- **Dependency Security**: Safety, pip-audit for dependency vulnerabilities
- **Code Security**: Bandit, Semgrep for code security issues
- **Docker Security**: Trivy for container vulnerability scanning
- **Secrets Detection**: TruffleHog for secret detection
- **Dependency Updates**: Automated dependency update notifications

### 5. Release (`release.yml`)
**Triggers**: Git tags (v*.*.*), Manual dispatch
**Purpose**: Create and deploy releases

**Jobs**:
- **Validate**: Validate release version format
- **Test**: Full test suite for release
- **Build**: Build Docker images and release artifacts
- **Deploy**: Deploy to production
- **GitHub Release**: Create GitHub release with changelog

## Required Secrets

Configure these secrets in your GitHub repository settings:

### Railway Deployment
- `RAILWAY_TOKEN`: Production Railway API token
- `RAILWAY_PREVIEW_TOKEN`: Preview environment Railway API token (optional)
- `RAILWAY_PRODUCTION_TOKEN`: Production-specific Railway token (for releases)

### Docker Hub (for releases)
- `DOCKER_USERNAME`: Docker Hub username
- `DOCKER_PASSWORD`: Docker Hub password or access token

### GitHub Token
- `GITHUB_TOKEN`: Automatically provided by GitHub Actions

## Environment Setup

### Local Development
1. Copy `.env.example` to `.env`
2. Fill in required environment variables
3. Use `scripts/docker-dev.sh start` to run locally

### Railway Production
1. Use `scripts/railway-setup.sh setup` for initial setup
2. Configure environment variables through Railway dashboard
3. Ensure database services (PostgreSQL, Redis) are added

## Workflow Features

### Automatic Testing
- All workflows run comprehensive tests before deployment
- Tests include unit tests, integration tests, and E2E tests
- Database migrations are tested in CI environment

### Security Scanning
- Daily security scans for dependencies and code
- Container vulnerability scanning with Trivy
- Secret detection to prevent credential leaks
- Automated security issue reporting

### Preview Deployments
- Automatic preview deployments for pull requests
- Preview environments are automatically cleaned up
- PR comments with preview links and test results

### Release Management
- Semantic versioning with git tags
- Automated changelog generation
- Docker image building and publishing
- Production deployment with health checks

## Usage Examples

### Creating a Release
```bash
# Create and push a version tag
git tag v1.0.0
git push origin v1.0.0

# Or use GitHub UI to create a release
```

### Manual Deployment
```bash
# Trigger manual deployment via GitHub Actions UI
# Go to Actions → Deploy to Railway → Run workflow
```

### Running Security Scans
```bash
# Security scans run automatically, but can be triggered manually
# Go to Actions → Security Scanning → Run workflow
```

## Monitoring and Notifications

### Deployment Status
- Deployment success/failure notifications in workflow logs
- Health checks verify successful deployments
- Rollback procedures documented in Railway guide

### Security Alerts
- Daily security scans create issues for vulnerabilities
- Dependency update notifications
- SARIF uploads to GitHub Security tab

### Performance Monitoring
- Prometheus metrics collection
- Health check endpoints monitored
- Resource usage tracking in Railway dashboard

## Troubleshooting

### Common Issues

1. **Test Failures**
   - Check database connection in CI
   - Verify environment variables are set correctly
   - Review test logs for specific failures

2. **Deployment Failures**
   - Verify Railway tokens are valid
   - Check Railway service status
   - Review deployment logs in Railway dashboard

3. **Security Scan Failures**
   - Review security reports in workflow artifacts
   - Update dependencies with known vulnerabilities
   - Fix code security issues identified by scanners

### Getting Help
- Check workflow logs in GitHub Actions tab
- Review Railway deployment logs
- Create issues for persistent problems
- Consult Railway documentation for deployment issues

## Best Practices

### Code Quality
- All code must pass linting and formatting checks
- Maintain test coverage above 80%
- Follow security best practices

### Deployment Safety
- Never deploy without passing tests
- Use preview environments for testing changes
- Monitor deployments with health checks

### Security
- Regularly update dependencies
- Review security scan results
- Use secrets management for sensitive data
- Follow principle of least privilege for tokens