import { apiClient } from '../apiClient';
import { HealthCheck } from '../../types';

export interface SystemMetrics {
  timestamp: string;
  api_requests_total: number;
  api_response_time_avg: number;
  active_tasks: number;
  database_connections: number;
  redis_memory_usage: number;
  crawling_success_rate: number;
  system_cpu_usage: number;
  system_memory_usage: number;
  system_disk_usage: number;
}

export interface SystemHealth {
  status: string;
  timestamp: string;
  services: {
    database: {
      status: string;
      response_time_ms?: number;
      error?: string;
    };
    redis: {
      status: string;
      response_time_ms?: number;
      error?: string;
    };
    celery: {
      status: string;
      active_workers?: number;
      workers?: string[];
      error?: string;
    };
  };
  overall_health_score: number;
}

export interface AlertInfo {
  id: string;
  type: 'warning' | 'error' | 'critical';
  title: string;
  message: string;
  timestamp: string;
  resolved: boolean;
}

export const systemApi = {
  // Get system health status
  getHealth: async (): Promise<HealthCheck> => {
    return apiClient.get<HealthCheck>('/api/v1/health');
  },

  // Get comprehensive system health
  getSystemHealth: async (): Promise<SystemHealth> => {
    return apiClient.get<SystemHealth>('/api/v1/system/health');
  },

  // Get system metrics
  getMetrics: async (params?: { time_range?: string }): Promise<SystemMetrics[]> => {
    return apiClient.get<SystemMetrics[]>('/api/v1/system/metrics', { params });
  },

  // Get system alerts
  getAlerts: async (params?: { resolved?: boolean }): Promise<AlertInfo[]> => {
    return apiClient.get<AlertInfo[]>('/api/v1/system/alerts', { params });
  },

  // Get application info
  getAppInfo: async () => {
    return apiClient.get('/api/v1/system/info');
  },
};