# Monitoring Dashboard Setup and Alert Configuration

## Overview

This document provides comprehensive instructions for setting up monitoring dashboards and alert configurations for the Reddit Content Platform. The monitoring stack includes Prometheus for metrics collection, Grafana for visualization, and Alertmanager for alert routing.

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Prometheus Setup](#prometheus-setup)
3. [Grafana Dashboard Configuration](#grafana-dashboard-configuration)
4. [Alertmanager Configuration](#alertmanager-configuration)
5. [Custom Metrics](#custom-metrics)
6. [Alert Rules](#alert-rules)
7. [Notification Channels](#notification-channels)
8. [Dashboard Templates](#dashboard-templates)
9. [Maintenance and Troubleshooting](#maintenance-and-troubleshooting)

## Architecture Overview

### Monitoring Stack Components

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Application   │    │   Exporters     │    │   Prometheus    │
│   (FastAPI)     │───▶│   (Various)     │───▶│   (Metrics)     │
│   Port: 8000    │    │   Ports: 91xx   │    │   Port: 9090    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                        │
                                                        ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Grafana       │◀───│   Alertmanager  │◀───│   Alert Rules   │
│   (Dashboard)   │    │   (Routing)     │    │   (Evaluation)  │
│   Port: 3000    │    │   Port: 9093    │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Metrics Collection Points

1. **Application Metrics**: FastAPI application performance
2. **System Metrics**: CPU, memory, disk, network
3. **Database Metrics**: PostgreSQL performance
4. **Cache Metrics**: Redis performance
5. **Queue Metrics**: Celery task processing
6. **Business Metrics**: Crawling success, content generation

## Prometheus Setup

### Enhanced Configuration

Create an enhanced Prometheus configuration:

```yaml
# monitoring/prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s
  external_labels:
    cluster: 'reddit-content-platform'
    environment: 'production'

rule_files:
  - "alert_rules.yml"
  - "recording_rules.yml"

alerting:
  alertmanagers:
    - static_configs:
        - targets:
          - alertmanager:9093
      timeout: 10s
      api_version: v2

scrape_configs:
  # FastAPI application metrics
  - job_name: 'reddit-content-platform-api'
    static_configs:
      - targets: ['api:8000']
    metrics_path: '/metrics'
    scrape_interval: 10s
    scrape_timeout: 5s
    honor_labels: true
    relabel_configs:
      - source_labels: [__address__]
        target_label: instance
        replacement: 'api-server'
    
  # System metrics
  - job_name: 'node-exporter'
    static_configs:
      - targets: ['node-exporter:9100']
    scrape_interval: 15s
    relabel_configs:
      - source_labels: [__address__]
        target_label: instance
        replacement: 'main-server'
    
  # PostgreSQL metrics
  - job_name: 'postgres-exporter'
    static_configs:
      - targets: ['postgres-exporter:9187']
    scrape_interval: 15s
    params:
      collect[]:
        - 'pg_stat_database'
        - 'pg_stat_user_tables'
        - 'pg_stat_activity'
    
  # Redis metrics
  - job_name: 'redis-exporter'
    static_configs:
      - targets: ['redis-exporter:9121']
    scrape_interval: 15s
    
  # Celery metrics
  - job_name: 'celery-exporter'
    static_configs:
      - targets: ['celery-exporter:9540']
    scrape_interval: 15s

  # Nginx metrics (if using nginx-prometheus-exporter)
  - job_name: 'nginx-exporter'
    static_configs:
      - targets: ['nginx-exporter:9113']
    scrape_interval: 15s

# Storage configuration
storage:
  tsdb:
    retention.time: 30d
    retention.size: 10GB
    wal-compression: true

# Remote write configuration (optional - for long-term storage)
# remote_write:
#   - url: "https://your-remote-storage/api/v1/write"
#     basic_auth:
#       username: "username"
#       password: "password"
```

### Recording Rules

Create recording rules for commonly used queries:

```yaml
# monitoring/recording_rules.yml
groups:
  - name: reddit_platform_recording_rules
    interval: 30s
    rules:
      # API Performance Rules
      - record: api:request_rate_5m
        expr: rate(api_requests_total[5m])
        
      - record: api:error_rate_5m
        expr: rate(api_requests_total{status_code=~"5.."}[5m])
        
      - record: api:latency_p95_5m
        expr: histogram_quantile(0.95, rate(api_request_duration_seconds_bucket[5m]))
        
      - record: api:latency_p99_5m
        expr: histogram_quantile(0.99, rate(api_request_duration_seconds_bucket[5m]))
      
      # Celery Performance Rules
      - record: celery:task_rate_5m
        expr: rate(celery_tasks_total[5m])
        
      - record: celery:failure_rate_5m
        expr: rate(celery_tasks_total{status="failure"}[5m])
        
      - record: celery:success_rate_5m
        expr: rate(celery_tasks_total{status="success"}[5m]) / rate(celery_tasks_total[5m])
      
      # Database Performance Rules
      - record: db:query_rate_5m
        expr: rate(database_queries_total[5m])
        
      - record: db:slow_query_rate_5m
        expr: rate(database_slow_queries_total[5m])
        
      - record: db:connection_utilization
        expr: database_active_connections / database_max_connections
      
      # Business Metrics Rules
      - record: business:crawling_success_rate_1h
        expr: rate(crawling_tasks_total{status="success"}[1h]) / rate(crawling_tasks_total[1h])
        
      - record: business:content_generation_rate_1h
        expr: rate(content_generated_total{status="success"}[1h])
        
      - record: business:posts_collected_rate_1h
        expr: rate(posts_collected_total[1h])
```

## Grafana Dashboard Configuration

### Dashboard Provisioning

Create dashboard provisioning configuration:

```yaml
# monitoring/grafana/provisioning/dashboards/dashboard.yml
apiVersion: 1

providers:
  - name: 'reddit-platform-dashboards'
    orgId: 1
    folder: 'Reddit Platform'
    type: file
    disableDeletion: false
    updateIntervalSeconds: 10
    allowUiUpdates: true
    options:
      path: /etc/grafana/provisioning/dashboards
```

### Data Source Configuration

```yaml
# monitoring/grafana/provisioning/datasources/prometheus.yml
apiVersion: 1

datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
    editable: true
    jsonData:
      timeInterval: "15s"
      queryTimeout: "60s"
      httpMethod: "POST"
```

### Main Dashboard JSON

Create the main dashboard configuration:

```json
{
  "dashboard": {
    "id": null,
    "title": "Reddit Content Platform - Overview",
    "tags": ["reddit-platform", "overview"],
    "timezone": "browser",
    "refresh": "30s",
    "time": {
      "from": "now-1h",
      "to": "now"
    },
    "panels": [
      {
        "id": 1,
        "title": "API Request Rate",
        "type": "stat",
        "targets": [
          {
            "expr": "sum(api:request_rate_5m)",
            "legendFormat": "Requests/sec"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "unit": "reqps",
            "color": {
              "mode": "thresholds"
            },
            "thresholds": {
              "steps": [
                {"color": "green", "value": null},
                {"color": "yellow", "value": 50},
                {"color": "red", "value": 100}
              ]
            }
          }
        },
        "gridPos": {"h": 8, "w": 6, "x": 0, "y": 0}
      },
      {
        "id": 2,
        "title": "API Error Rate",
        "type": "stat",
        "targets": [
          {
            "expr": "sum(api:error_rate_5m)",
            "legendFormat": "Errors/sec"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "unit": "reqps",
            "color": {
              "mode": "thresholds"
            },
            "thresholds": {
              "steps": [
                {"color": "green", "value": null},
                {"color": "yellow", "value": 0.1},
                {"color": "red", "value": 1}
              ]
            }
          }
        },
        "gridPos": {"h": 8, "w": 6, "x": 6, "y": 0}
      },
      {
        "id": 3,
        "title": "API Latency (95th percentile)",
        "type": "stat",
        "targets": [
          {
            "expr": "api:latency_p95_5m",
            "legendFormat": "P95 Latency"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "unit": "s",
            "color": {
              "mode": "thresholds"
            },
            "thresholds": {
              "steps": [
                {"color": "green", "value": null},
                {"color": "yellow", "value": 0.5},
                {"color": "red", "value": 2}
              ]
            }
          }
        },
        "gridPos": {"h": 8, "w": 6, "x": 12, "y": 0}
      },
      {
        "id": 4,
        "title": "Active Celery Tasks",
        "type": "stat",
        "targets": [
          {
            "expr": "celery_active_tasks",
            "legendFormat": "Active Tasks"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "unit": "short",
            "color": {
              "mode": "thresholds"
            },
            "thresholds": {
              "steps": [
                {"color": "green", "value": null},
                {"color": "yellow", "value": 50},
                {"color": "red", "value": 100}
              ]
            }
          }
        },
        "gridPos": {"h": 8, "w": 6, "x": 18, "y": 0}
      },
      {
        "id": 5,
        "title": "API Request Rate Over Time",
        "type": "graph",
        "targets": [
          {
            "expr": "sum by (endpoint) (api:request_rate_5m)",
            "legendFormat": "{{endpoint}}"
          }
        ],
        "yAxes": [
          {
            "label": "Requests/sec",
            "min": 0
          }
        ],
        "gridPos": {"h": 8, "w": 12, "x": 0, "y": 8}
      },
      {
        "id": 6,
        "title": "Response Time Distribution",
        "type": "graph",
        "targets": [
          {
            "expr": "histogram_quantile(0.50, rate(api_request_duration_seconds_bucket[5m]))",
            "legendFormat": "P50"
          },
          {
            "expr": "histogram_quantile(0.95, rate(api_request_duration_seconds_bucket[5m]))",
            "legendFormat": "P95"
          },
          {
            "expr": "histogram_quantile(0.99, rate(api_request_duration_seconds_bucket[5m]))",
            "legendFormat": "P99"
          }
        ],
        "yAxes": [
          {
            "label": "Seconds",
            "min": 0
          }
        ],
        "gridPos": {"h": 8, "w": 12, "x": 12, "y": 8}
      }
    ]
  }
}
```

### Business Metrics Dashboard

Create a business-focused dashboard:

```json
{
  "dashboard": {
    "id": null,
    "title": "Reddit Content Platform - Business Metrics",
    "tags": ["reddit-platform", "business"],
    "timezone": "browser",
    "refresh": "1m",
    "time": {
      "from": "now-24h",
      "to": "now"
    },
    "panels": [
      {
        "id": 1,
        "title": "Crawling Success Rate",
        "type": "stat",
        "targets": [
          {
            "expr": "business:crawling_success_rate_1h * 100",
            "legendFormat": "Success Rate %"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "unit": "percent",
            "min": 0,
            "max": 100,
            "color": {
              "mode": "thresholds"
            },
            "thresholds": {
              "steps": [
                {"color": "red", "value": null},
                {"color": "yellow", "value": 70},
                {"color": "green", "value": 90}
              ]
            }
          }
        },
        "gridPos": {"h": 8, "w": 6, "x": 0, "y": 0}
      },
      {
        "id": 2,
        "title": "Posts Collected (Last 24h)",
        "type": "stat",
        "targets": [
          {
            "expr": "increase(posts_collected_total[24h])",
            "legendFormat": "Posts"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "unit": "short",
            "color": {
              "mode": "palette-classic"
            }
          }
        },
        "gridPos": {"h": 8, "w": 6, "x": 6, "y": 0}
      },
      {
        "id": 3,
        "title": "Content Generated (Last 24h)",
        "type": "stat",
        "targets": [
          {
            "expr": "increase(content_generated_total{status=\"success\"}[24h])",
            "legendFormat": "Articles"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "unit": "short",
            "color": {
              "mode": "palette-classic"
            }
          }
        },
        "gridPos": {"h": 8, "w": 6, "x": 12, "y": 0}
      },
      {
        "id": 4,
        "title": "Active Keywords",
        "type": "stat",
        "targets": [
          {
            "expr": "keywords_active_total",
            "legendFormat": "Keywords"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "unit": "short",
            "color": {
              "mode": "palette-classic"
            }
          }
        },
        "gridPos": {"h": 8, "w": 6, "x": 18, "y": 0}
      }
    ]
  }
}
```

## Alertmanager Configuration

### Main Configuration

```yaml
# monitoring/alertmanager.yml
global:
  smtp_smarthost: 'localhost:587'
  smtp_from: 'alerts@yourplatform.com'
  smtp_auth_username: 'alerts@yourplatform.com'
  smtp_auth_password: 'your-email-password'

route:
  group_by: ['alertname', 'cluster', 'service']
  group_wait: 10s
  group_interval: 10s
  repeat_interval: 1h
  receiver: 'default-receiver'
  routes:
    - match:
        severity: critical
      receiver: 'critical-alerts'
      group_wait: 5s
      repeat_interval: 30m
    - match:
        severity: warning
      receiver: 'warning-alerts'
      repeat_interval: 2h
    - match:
        alertname: 'RedditAPIRateLimit'
      receiver: 'reddit-api-alerts'
      group_wait: 1s
      repeat_interval: 15m

receivers:
  - name: 'default-receiver'
    email_configs:
      - to: 'admin@yourplatform.com'
        subject: '[Reddit Platform] Alert: {{ .GroupLabels.alertname }}'
        body: |
          {{ range .Alerts }}
          Alert: {{ .Annotations.summary }}
          Description: {{ .Annotations.description }}
          Labels: {{ range .Labels.SortedPairs }}{{ .Name }}={{ .Value }} {{ end }}
          {{ end }}

  - name: 'critical-alerts'
    email_configs:
      - to: 'admin@yourplatform.com,oncall@yourplatform.com'
        subject: '[CRITICAL] Reddit Platform Alert: {{ .GroupLabels.alertname }}'
        body: |
          🚨 CRITICAL ALERT 🚨
          
          {{ range .Alerts }}
          Alert: {{ .Annotations.summary }}
          Description: {{ .Annotations.description }}
          Severity: {{ .Labels.severity }}
          Time: {{ .StartsAt }}
          Labels: {{ range .Labels.SortedPairs }}{{ .Name }}={{ .Value }} {{ end }}
          {{ end }}
    slack_configs:
      - api_url: 'https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK'
        channel: '#alerts-critical'
        title: 'Critical Alert: {{ .GroupLabels.alertname }}'
        text: |
          {{ range .Alerts }}
          {{ .Annotations.summary }}
          {{ .Annotations.description }}
          {{ end }}
        color: 'danger'

  - name: 'warning-alerts'
    email_configs:
      - to: 'admin@yourplatform.com'
        subject: '[WARNING] Reddit Platform Alert: {{ .GroupLabels.alertname }}'
        body: |
          ⚠️ WARNING ALERT ⚠️
          
          {{ range .Alerts }}
          Alert: {{ .Annotations.summary }}
          Description: {{ .Annotations.description }}
          Severity: {{ .Labels.severity }}
          Time: {{ .StartsAt }}
          {{ end }}
    slack_configs:
      - api_url: 'https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK'
        channel: '#alerts-warning'
        title: 'Warning: {{ .GroupLabels.alertname }}'
        text: |
          {{ range .Alerts }}
          {{ .Annotations.summary }}
          {{ end }}
        color: 'warning'

  - name: 'reddit-api-alerts'
    slack_configs:
      - api_url: 'https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK'
        channel: '#reddit-api'
        title: 'Reddit API Alert: {{ .GroupLabels.alertname }}'
        text: |
          {{ range .Alerts }}
          {{ .Annotations.summary }}
          {{ .Annotations.description }}
          {{ end }}
        color: 'warning'

inhibit_rules:
  - source_match:
      severity: 'critical'
    target_match:
      severity: 'warning'
    equal: ['alertname', 'cluster', 'service']
```

### Notification Templates

Create custom notification templates:

```yaml
# monitoring/notification_templates.yml
templates:
  - '/etc/alertmanager/templates/*.tmpl'
```

```html
<!-- monitoring/templates/email.tmpl -->
{{ define "email.subject" }}
[{{ .Status | toUpper }}{{ if eq .Status "firing" }}:{{ .Alerts.Firing | len }}{{ end }}] Reddit Platform Alert
{{ end }}

{{ define "email.html" }}
<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: Arial, sans-serif; }
        .alert { margin: 10px 0; padding: 10px; border-left: 4px solid; }
        .critical { border-color: #d32f2f; background-color: #ffebee; }
        .warning { border-color: #f57c00; background-color: #fff3e0; }
        .resolved { border-color: #388e3c; background-color: #e8f5e8; }
    </style>
</head>
<body>
    <h2>Reddit Content Platform Alert</h2>
    
    {{ if gt (len .Alerts.Firing) 0 }}
    <h3>🔥 Firing Alerts ({{ .Alerts.Firing | len }})</h3>
    {{ range .Alerts.Firing }}
    <div class="alert {{ .Labels.severity }}">
        <h4>{{ .Annotations.summary }}</h4>
        <p><strong>Description:</strong> {{ .Annotations.description }}</p>
        <p><strong>Started:</strong> {{ .StartsAt.Format "2006-01-02 15:04:05 UTC" }}</p>
        <p><strong>Labels:</strong>
        {{ range .Labels.SortedPairs }}
            <span>{{ .Name }}={{ .Value }}</span>
        {{ end }}
        </p>
    </div>
    {{ end }}
    {{ end }}
    
    {{ if gt (len .Alerts.Resolved) 0 }}
    <h3>✅ Resolved Alerts ({{ .Alerts.Resolved | len }})</h3>
    {{ range .Alerts.Resolved }}
    <div class="alert resolved">
        <h4>{{ .Annotations.summary }}</h4>
        <p><strong>Resolved:</strong> {{ .EndsAt.Format "2006-01-02 15:04:05 UTC" }}</p>
        <p><strong>Duration:</strong> {{ .EndsAt.Sub .StartsAt }}</p>
    </div>
    {{ end }}
    {{ end }}
</body>
</html>
{{ end }}
```

## Custom Metrics

### Application Metrics

Enhance the application metrics collection:

```python
# app/core/metrics.py
from prometheus_client import Counter, Histogram, Gauge, Info
import time
from functools import wraps

# API Metrics
api_requests_total = Counter(
    'api_requests_total',
    'Total API requests',
    ['method', 'endpoint', 'status_code']
)

api_request_duration_seconds = Histogram(
    'api_request_duration_seconds',
    'API request duration',
    ['method', 'endpoint'],
    buckets=[0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0]
)

# Business Metrics
posts_collected_total = Counter(
    'posts_collected_total',
    'Total posts collected',
    ['keyword', 'subreddit']
)

content_generated_total = Counter(
    'content_generated_total',
    'Total content generated',
    ['template', 'status']
)

crawling_tasks_total = Counter(
    'crawling_tasks_total',
    'Total crawling tasks',
    ['keyword', 'status']
)

keywords_active_total = Gauge(
    'keywords_active_total',
    'Number of active keywords'
)

# System Metrics
system_info = Info(
    'system_info',
    'System information'
)

# Reddit API Metrics
reddit_api_calls_total = Counter(
    'reddit_api_calls_total',
    'Total Reddit API calls',
    ['endpoint', 'status']
)

reddit_api_rate_limit_remaining = Gauge(
    'reddit_api_rate_limit_remaining',
    'Reddit API rate limit remaining'
)

# Database Metrics
database_queries_total = Counter(
    'database_queries_total',
    'Total database queries',
    ['operation', 'table']
)

database_query_duration_seconds = Histogram(
    'database_query_duration_seconds',
    'Database query duration',
    ['operation', 'table'],
    buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0]
)

database_connections_active = Gauge(
    'database_connections_active',
    'Active database connections'
)

# Celery Metrics
celery_tasks_total = Counter(
    'celery_tasks_total',
    'Total Celery tasks',
    ['task_name', 'status']
)

celery_task_duration_seconds = Histogram(
    'celery_task_duration_seconds',
    'Celery task duration',
    ['task_name'],
    buckets=[1, 5, 10, 30, 60, 300, 600, 1800]
)

celery_active_tasks = Gauge(
    'celery_active_tasks',
    'Active Celery tasks',
    ['queue']
)

# Decorators for automatic metrics collection
def track_api_metrics(endpoint: str):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            status_code = 200
            
            try:
                result = await func(*args, **kwargs)
                return result
            except Exception as e:
                status_code = getattr(e, 'status_code', 500)
                raise
            finally:
                duration = time.time() - start_time
                api_requests_total.labels(
                    method='GET',  # This should be extracted from request
                    endpoint=endpoint,
                    status_code=status_code
                ).inc()
                api_request_duration_seconds.labels(
                    method='GET',
                    endpoint=endpoint
                ).observe(duration)
        
        return wrapper
    return decorator

def track_celery_task(task_name: str):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            status = 'success'
            
            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                status = 'failure'
                raise
            finally:
                duration = time.time() - start_time
                celery_tasks_total.labels(
                    task_name=task_name,
                    status=status
                ).inc()
                celery_task_duration_seconds.labels(
                    task_name=task_name
                ).observe(duration)
        
        return wrapper
    return decorator
```

## Alert Rules

### Enhanced Alert Rules

Update the alert rules with more comprehensive coverage:

```yaml
# monitoring/alert_rules.yml
groups:
  - name: reddit_platform_sla_alerts
    rules:
      # SLA-based alerts
      - alert: APIAvailabilityLow
        expr: (1 - (rate(api_requests_total{status_code=~"5.."}[5m]) / rate(api_requests_total[5m]))) * 100 < 99.9
        for: 2m
        labels:
          severity: critical
          sla: availability
        annotations:
          summary: "API availability below SLA"
          description: "API availability is {{ $value }}% (SLA: 99.9%)"
          runbook_url: "https://docs.yourplatform.com/runbooks/api-availability"

      - alert: APILatencyHigh
        expr: histogram_quantile(0.95, rate(api_request_duration_seconds_bucket[5m])) > 2
        for: 5m
        labels:
          severity: warning
          sla: latency
        annotations:
          summary: "API latency above SLA"
          description: "95th percentile latency is {{ $value }}s (SLA: 2s)"
          runbook_url: "https://docs.yourplatform.com/runbooks/api-latency"

  - name: reddit_platform_business_alerts
    rules:
      # Business logic alerts
      - alert: CrawlingSuccessRateLow
        expr: business:crawling_success_rate_1h * 100 < 80
        for: 15m
        labels:
          severity: warning
          category: business
        annotations:
          summary: "Crawling success rate is low"
          description: "Crawling success rate is {{ $value }}% (threshold: 80%)"
          impact: "New content collection may be affected"

      - alert: NoContentGeneratedRecently
        expr: increase(content_generated_total{status="success"}[2h]) == 0
        for: 2h
        labels:
          severity: warning
          category: business
        annotations:
          summary: "No content generated in the last 2 hours"
          description: "Content generation pipeline may be stuck"
          impact: "Blog content updates may be delayed"

      - alert: RedditAPIQuotaExhausted
        expr: reddit_api_rate_limit_remaining < 10
        for: 1m
        labels:
          severity: critical
          category: external
        annotations:
          summary: "Reddit API quota nearly exhausted"
          description: "Only {{ $value }} Reddit API calls remaining"
          impact: "Crawling operations will be throttled"

  - name: reddit_platform_infrastructure_alerts
    rules:
      # Infrastructure alerts
      - alert: DatabaseConnectionPoolExhausted
        expr: database_connections_active / database_connections_max > 0.9
        for: 5m
        labels:
          severity: critical
          category: infrastructure
        annotations:
          summary: "Database connection pool nearly exhausted"
          description: "{{ $value | humanizePercentage }} of database connections in use"
          impact: "New database connections may fail"

      - alert: CeleryQueueBacklogHigh
        expr: celery_active_tasks > 100
        for: 10m
        labels:
          severity: warning
          category: infrastructure
        annotations:
          summary: "High Celery queue backlog"
          description: "{{ $value }} tasks in queue"
          impact: "Background task processing may be delayed"

      - alert: DiskSpaceLow
        expr: (node_filesystem_avail_bytes / node_filesystem_size_bytes) * 100 < 10
        for: 5m
        labels:
          severity: critical
          category: infrastructure
        annotations:
          summary: "Disk space critically low"
          description: "Only {{ $value | humanizePercentage }} disk space remaining on {{ $labels.mountpoint }}"
          impact: "System may become unstable"

  - name: reddit_platform_security_alerts
    rules:
      # Security-related alerts
      - alert: HighFailedAuthenticationRate
        expr: rate(api_requests_total{status_code="401"}[5m]) > 0.1
        for: 2m
        labels:
          severity: warning
          category: security
        annotations:
          summary: "High failed authentication rate"
          description: "{{ $value }} failed authentication attempts per second"
          impact: "Possible brute force attack"

      - alert: UnusualTrafficPattern
        expr: rate(api_requests_total[5m]) > 2 * rate(api_requests_total[1h] offset 1h)
        for: 10m
        labels:
          severity: warning
          category: security
        annotations:
          summary: "Unusual traffic pattern detected"
          description: "Current request rate is {{ $value }}x higher than usual"
          impact: "Possible DDoS attack or traffic spike"
```

## Notification Channels

### Slack Integration

Set up Slack notifications:

```yaml
# monitoring/slack_config.yml
slack_configs:
  - api_url: 'https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK'
    channel: '#alerts'
    username: 'Prometheus'
    icon_emoji: ':warning:'
    title: 'Alert: {{ .GroupLabels.alertname }}'
    text: |
      {{ range .Alerts }}
      *Alert:* {{ .Annotations.summary }}
      *Description:* {{ .Annotations.description }}
      *Severity:* {{ .Labels.severity }}
      *Time:* {{ .StartsAt.Format "2006-01-02 15:04:05 UTC" }}
      {{ if .Labels.runbook_url }}*Runbook:* {{ .Labels.runbook_url }}{{ end }}
      {{ end }}
    actions:
      - type: button
        text: 'View in Grafana'
        url: 'https://grafana.yourplatform.com/d/overview'
      - type: button
        text: 'Silence Alert'
        url: 'https://alertmanager.yourplatform.com/#/silences/new'
```

### PagerDuty Integration

Configure PagerDuty for critical alerts:

```yaml
# monitoring/pagerduty_config.yml
pagerduty_configs:
  - routing_key: 'YOUR_PAGERDUTY_INTEGRATION_KEY'
    description: 'Reddit Platform Alert: {{ .GroupLabels.alertname }}'
    details:
      alert_name: '{{ .GroupLabels.alertname }}'
      severity: '{{ .CommonLabels.severity }}'
      summary: '{{ range .Alerts }}{{ .Annotations.summary }}{{ end }}'
      description: '{{ range .Alerts }}{{ .Annotations.description }}{{ end }}'
      firing_alerts: '{{ .Alerts.Firing | len }}'
      resolved_alerts: '{{ .Alerts.Resolved | len }}'
```

### Discord Integration

Set up Discord notifications:

```yaml
# monitoring/discord_config.yml
discord_configs:
  - webhook_url: 'https://discord.com/api/webhooks/YOUR/WEBHOOK/URL'
    title: 'Reddit Platform Alert'
    message: |
      {{ range .Alerts }}
      **{{ .Annotations.summary }}**
      {{ .Annotations.description }}
      Severity: {{ .Labels.severity }}
      {{ end }}
```

## Dashboard Templates

### System Overview Dashboard

Create a comprehensive system overview:

```json
{
  "dashboard": {
    "title": "Reddit Platform - System Overview",
    "panels": [
      {
        "title": "System Health Score",
        "type": "stat",
        "targets": [
          {
            "expr": "(\n  (1 - rate(api_requests_total{status_code=~\"5..\"}[5m]) / rate(api_requests_total[5m])) * 0.4 +\n  (1 - rate(celery_tasks_total{status=\"failure\"}[5m]) / rate(celery_tasks_total[5m])) * 0.3 +\n  (database_connections_active / database_connections_max < 0.8) * 0.3\n) * 100",
            "legendFormat": "Health Score"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "unit": "percent",
            "min": 0,
            "max": 100,
            "thresholds": {
              "steps": [
                {"color": "red", "value": 0},
                {"color": "yellow", "value": 70},
                {"color": "green", "value": 90}
              ]
            }
          }
        }
      }
    ]
  }
}
```

## Maintenance and Troubleshooting

### Regular Maintenance Tasks

Create maintenance scripts:

```bash
#!/bin/bash
# scripts/monitoring_maintenance.sh

echo "Starting monitoring maintenance..."

# Clean up old Prometheus data
docker exec prometheus promtool tsdb cleanup --retention.time=30d /prometheus

# Restart Grafana to clear cache
docker restart grafana

# Check alert rules syntax
docker exec prometheus promtool check rules /etc/prometheus/alert_rules.yml

# Test alertmanager configuration
docker exec alertmanager amtool config check /etc/alertmanager/alertmanager.yml

# Generate monitoring health report
python scripts/monitoring_health_check.py

echo "Monitoring maintenance completed."
```

### Troubleshooting Guide

```python
#!/usr/bin/env python3
# scripts/monitoring_health_check.py

import requests
import json
from datetime import datetime

def check_prometheus():
    try:
        response = requests.get('http://localhost:9090/-/healthy', timeout=5)
        return response.status_code == 200
    except:
        return False

def check_grafana():
    try:
        response = requests.get('http://localhost:3000/api/health', timeout=5)
        return response.status_code == 200
    except:
        return False

def check_alertmanager():
    try:
        response = requests.get('http://localhost:9093/-/healthy', timeout=5)
        return response.status_code == 200
    except:
        return False

def main():
    health_status = {
        'timestamp': datetime.utcnow().isoformat(),
        'prometheus': check_prometheus(),
        'grafana': check_grafana(),
        'alertmanager': check_alertmanager()
    }
    
    print(json.dumps(health_status, indent=2))
    
    if all(health_status.values()):
        print("✅ All monitoring services are healthy")
        return 0
    else:
        print("❌ Some monitoring services are unhealthy")
        return 1

if __name__ == '__main__':
    exit(main())
```

### Common Issues and Solutions

1. **Prometheus not scraping targets**
   - Check network connectivity
   - Verify target endpoints are accessible
   - Check Prometheus configuration syntax

2. **Grafana dashboards not loading**
   - Verify data source configuration
   - Check Prometheus connectivity from Grafana
   - Review dashboard JSON syntax

3. **Alerts not firing**
   - Verify alert rule syntax
   - Check if metrics are being collected
   - Review alertmanager configuration

4. **High memory usage**
   - Adjust Prometheus retention settings
   - Optimize query performance
   - Consider using recording rules

---

**Document Version**: 1.0.0  
**Last Updated**: 2025-08-03  
**Monitoring Stack**: Prometheus + Grafana + Alertmanager  
**Review Schedule**: Monthly