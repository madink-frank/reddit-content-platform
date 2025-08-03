#!/usr/bin/env python3
"""
Performance testing script for Reddit Content Platform.
"""

import asyncio
import time
import statistics
import json
import argparse
from typing import List, Dict, Any
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
import psutil
import sys
import os

# Add app to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import get_db_session
from app.core.redis_client import redis_client
from app.services.post_service import PostService
from app.services.keyword_service import KeywordService
from app.services.trend_analysis_service import TrendAnalysisService


class PerformanceTester:
    """Performance testing utilities."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.results = {}
    
    def test_api_endpoints(self, num_requests: int = 100) -> Dict[str, Any]:
        """Test API endpoint performance."""
        endpoints = [
            {"method": "GET", "path": "/health"},
            {"method": "GET", "path": "/api/v1/posts", "params": {"page": 1, "per_page": 20}},
            {"method": "GET", "path": "/api/v1/keywords", "params": {"limit": 50}},
            {"method": "GET", "path": "/api/v1/public-blog/posts", "params": {"page": 1}},
        ]
        
        results = {}
        
        for endpoint in endpoints:
            print(f"Testing {endpoint['method']} {endpoint['path']}...")
            
            response_times = []
            errors = 0
            
            for i in range(num_requests):
                start_time = time.time()
                
                try:
                    url = f"{self.base_url}{endpoint['path']}"
                    params = endpoint.get('params', {})
                    
                    if endpoint['method'] == 'GET':
                        response = self.session.get(url, params=params, timeout=10)
                    else:
                        response = self.session.request(endpoint['method'], url, timeout=10)
                    
                    response_time = (time.time() - start_time) * 1000  # Convert to ms
                    
                    if response.status_code == 200:
                        response_times.append(response_time)
                    else:
                        errors += 1
                        
                except Exception as e:
                    errors += 1
                    print(f"Request {i+1} failed: {e}")
                
                # Progress indicator
                if (i + 1) % 10 == 0:
                    print(f"  Completed {i+1}/{num_requests} requests")
            
            if response_times:
                results[f"{endpoint['method']} {endpoint['path']}"] = {
                    "total_requests": num_requests,
                    "successful_requests": len(response_times),
                    "errors": errors,
                    "avg_response_time_ms": statistics.mean(response_times),
                    "median_response_time_ms": statistics.median(response_times),
                    "min_response_time_ms": min(response_times),
                    "max_response_time_ms": max(response_times),
                    "p95_response_time_ms": self._percentile(response_times, 95),
                    "p99_response_time_ms": self._percentile(response_times, 99),
                    "requests_per_second": len(response_times) / (max(response_times) / 1000) if response_times else 0
                }
            else:
                results[f"{endpoint['method']} {endpoint['path']}"] = {
                    "total_requests": num_requests,
                    "successful_requests": 0,
                    "errors": errors,
                    "error_rate": 100.0
                }
        
        return results
    
    def test_database_performance(self, num_queries: int = 50) -> Dict[str, Any]:
        """Test database query performance."""
        print(f"Testing database performance with {num_queries} queries...")
        
        results = {}
        
        # Test different query types
        query_tests = [
            ("get_posts_paginated", self._test_posts_query),
            ("get_user_keywords", self._test_keywords_query),
            ("analyze_trends", self._test_trends_query),
        ]
        
        for test_name, test_func in query_tests:
            print(f"  Testing {test_name}...")
            
            response_times = []
            errors = 0
            
            for i in range(num_queries):
                start_time = time.time()
                
                try:
                    test_func()
                    response_time = (time.time() - start_time) * 1000
                    response_times.append(response_time)
                except Exception as e:
                    errors += 1
                    print(f"    Query {i+1} failed: {e}")
            
            if response_times:
                results[test_name] = {
                    "total_queries": num_queries,
                    "successful_queries": len(response_times),
                    "errors": errors,
                    "avg_response_time_ms": statistics.mean(response_times),
                    "median_response_time_ms": statistics.median(response_times),
                    "min_response_time_ms": min(response_times),
                    "max_response_time_ms": max(response_times),
                    "p95_response_time_ms": self._percentile(response_times, 95)
                }
        
        return results
    
    def test_redis_performance(self, num_operations: int = 1000) -> Dict[str, Any]:
        """Test Redis cache performance."""
        print(f"Testing Redis performance with {num_operations} operations...")
        
        results = {}
        
        # Test different Redis operations
        operations = [
            ("set", self._test_redis_set),
            ("get", self._test_redis_get),
            ("delete", self._test_redis_delete),
        ]
        
        for op_name, op_func in operations:
            print(f"  Testing Redis {op_name}...")
            
            response_times = []
            errors = 0
            
            for i in range(num_operations):
                start_time = time.time()
                
                try:
                    asyncio.run(op_func(f"test_key_{i}"))
                    response_time = (time.time() - start_time) * 1000
                    response_times.append(response_time)
                except Exception as e:
                    errors += 1
            
            if response_times:
                results[f"redis_{op_name}"] = {
                    "total_operations": num_operations,
                    "successful_operations": len(response_times),
                    "errors": errors,
                    "avg_response_time_ms": statistics.mean(response_times),
                    "median_response_time_ms": statistics.median(response_times),
                    "operations_per_second": len(response_times) / (sum(response_times) / 1000) if response_times else 0
                }
        
        return results
    
    def test_concurrent_load(self, num_threads: int = 10, requests_per_thread: int = 50) -> Dict[str, Any]:
        """Test concurrent load performance."""
        print(f"Testing concurrent load with {num_threads} threads, {requests_per_thread} requests each...")
        
        def worker_thread(thread_id: int) -> List[float]:
            """Worker thread for concurrent testing."""
            response_times = []
            
            for i in range(requests_per_thread):
                start_time = time.time()
                
                try:
                    response = self.session.get(f"{self.base_url}/health", timeout=10)
                    response_time = (time.time() - start_time) * 1000
                    
                    if response.status_code == 200:
                        response_times.append(response_time)
                        
                except Exception:
                    pass  # Count as failed request
            
            return response_times
        
        # Execute concurrent requests
        all_response_times = []
        errors = 0
        
        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [executor.submit(worker_thread, i) for i in range(num_threads)]
            
            for future in as_completed(futures):
                try:
                    thread_times = future.result()
                    all_response_times.extend(thread_times)
                except Exception as e:
                    errors += 1
                    print(f"Thread failed: {e}")
        
        total_requests = num_threads * requests_per_thread
        successful_requests = len(all_response_times)
        
        if all_response_times:
            return {
                "concurrent_load": {
                    "num_threads": num_threads,
                    "requests_per_thread": requests_per_thread,
                    "total_requests": total_requests,
                    "successful_requests": successful_requests,
                    "failed_requests": total_requests - successful_requests,
                    "success_rate_percent": (successful_requests / total_requests) * 100,
                    "avg_response_time_ms": statistics.mean(all_response_times),
                    "median_response_time_ms": statistics.median(all_response_times),
                    "p95_response_time_ms": self._percentile(all_response_times, 95),
                    "p99_response_time_ms": self._percentile(all_response_times, 99),
                    "requests_per_second": successful_requests / (max(all_response_times) / 1000) if all_response_times else 0
                }
            }
        else:
            return {
                "concurrent_load": {
                    "error": "All requests failed",
                    "total_requests": total_requests,
                    "failed_requests": total_requests
                }
            }
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """Get current system performance metrics."""
        return {
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_usage_percent": psutil.disk_usage('/').percent,
            "load_average": os.getloadavg() if hasattr(os, 'getloadavg') else None,
            "process_count": len(psutil.pids()),
        }
    
    def _test_posts_query(self):
        """Test posts query performance."""
        with get_db_session() as db:
            service = PostService(db)
            # Simulate a typical posts query
            asyncio.run(service.get_posts_paginated(
                user_id=1,
                query_params=type('QueryParams', (), {
                    'page': 1,
                    'per_page': 20,
                    'keyword_id': None,
                    'search': None,
                    'sort_by': 'created_at',
                    'sort_order': 'desc',
                    'subreddit': None,
                    'author': None,
                    'min_score': None,
                    'max_score': None,
                    'date_from': None,
                    'date_to': None
                })()
            ))
    
    def _test_keywords_query(self):
        """Test keywords query performance."""
        with get_db_session() as db:
            service = KeywordService(db)
            asyncio.run(service.get_user_keywords(user_id=1, limit=50))
    
    def _test_trends_query(self):
        """Test trends analysis performance."""
        with get_db_session() as db:
            service = TrendAnalysisService()
            asyncio.run(service.analyze_keyword_trends(keyword_id=1, db=db))
    
    async def _test_redis_set(self, key: str):
        """Test Redis SET operation."""
        await redis_client.set_json(key, {"test": "data", "timestamp": time.time()}, 300)
    
    async def _test_redis_get(self, key: str):
        """Test Redis GET operation."""
        await redis_client.get_json(key)
    
    async def _test_redis_delete(self, key: str):
        """Test Redis DELETE operation."""
        await redis_client.delete(key)
    
    def _percentile(self, data: List[float], percentile: int) -> float:
        """Calculate percentile of data."""
        if not data:
            return 0.0
        
        sorted_data = sorted(data)
        index = int((percentile / 100) * len(sorted_data))
        
        if index >= len(sorted_data):
            return sorted_data[-1]
        
        return sorted_data[index]
    
    def run_full_performance_test(self) -> Dict[str, Any]:
        """Run complete performance test suite."""
        print("Starting full performance test suite...")
        
        results = {
            "test_timestamp": time.time(),
            "system_metrics_before": self.get_system_metrics()
        }
        
        # API endpoint tests
        print("\n1. Testing API endpoints...")
        results["api_endpoints"] = self.test_api_endpoints(num_requests=50)
        
        # Database performance tests
        print("\n2. Testing database performance...")
        results["database_performance"] = self.test_database_performance(num_queries=30)
        
        # Redis performance tests
        print("\n3. Testing Redis performance...")
        results["redis_performance"] = self.test_redis_performance(num_operations=500)
        
        # Concurrent load tests
        print("\n4. Testing concurrent load...")
        results["concurrent_load"] = self.test_concurrent_load(num_threads=5, requests_per_thread=20)
        
        # Final system metrics
        results["system_metrics_after"] = self.get_system_metrics()
        
        print("\nPerformance test suite completed!")
        return results
    
    def save_results(self, results: Dict[str, Any], filename: str = None):
        """Save test results to file."""
        if filename is None:
            timestamp = int(time.time())
            filename = f"performance_test_results_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        print(f"Results saved to {filename}")
    
    def print_summary(self, results: Dict[str, Any]):
        """Print test results summary."""
        print("\n" + "="*60)
        print("PERFORMANCE TEST SUMMARY")
        print("="*60)
        
        # API endpoints summary
        if "api_endpoints" in results:
            print("\nAPI Endpoints:")
            for endpoint, stats in results["api_endpoints"].items():
                if "avg_response_time_ms" in stats:
                    print(f"  {endpoint}:")
                    print(f"    Avg Response Time: {stats['avg_response_time_ms']:.2f}ms")
                    print(f"    Success Rate: {(stats['successful_requests']/stats['total_requests']*100):.1f}%")
                    print(f"    P95 Response Time: {stats['p95_response_time_ms']:.2f}ms")
        
        # Database performance summary
        if "database_performance" in results:
            print("\nDatabase Performance:")
            for query_type, stats in results["database_performance"].items():
                if "avg_response_time_ms" in stats:
                    print(f"  {query_type}:")
                    print(f"    Avg Query Time: {stats['avg_response_time_ms']:.2f}ms")
                    print(f"    Success Rate: {(stats['successful_queries']/stats['total_queries']*100):.1f}%")
        
        # Redis performance summary
        if "redis_performance" in results:
            print("\nRedis Performance:")
            for op_type, stats in results["redis_performance"].items():
                if "avg_response_time_ms" in stats:
                    print(f"  {op_type}:")
                    print(f"    Avg Operation Time: {stats['avg_response_time_ms']:.2f}ms")
                    print(f"    Operations/sec: {stats['operations_per_second']:.0f}")
        
        # System metrics
        if "system_metrics_after" in results:
            metrics = results["system_metrics_after"]
            print(f"\nSystem Metrics:")
            print(f"  CPU Usage: {metrics['cpu_percent']:.1f}%")
            print(f"  Memory Usage: {metrics['memory_percent']:.1f}%")
            print(f"  Disk Usage: {metrics['disk_usage_percent']:.1f}%")


def main():
    """Main function for command-line usage."""
    parser = argparse.ArgumentParser(description="Reddit Content Platform Performance Tester")
    parser.add_argument("--base-url", default="http://localhost:8000", help="Base URL for API testing")
    parser.add_argument("--output", help="Output file for results")
    parser.add_argument("--api-requests", type=int, default=50, help="Number of API requests per endpoint")
    parser.add_argument("--db-queries", type=int, default=30, help="Number of database queries per test")
    parser.add_argument("--redis-ops", type=int, default=500, help="Number of Redis operations per test")
    parser.add_argument("--threads", type=int, default=5, help="Number of concurrent threads")
    parser.add_argument("--requests-per-thread", type=int, default=20, help="Requests per thread")
    
    args = parser.parse_args()
    
    tester = PerformanceTester(base_url=args.base_url)
    
    print(f"Starting performance tests against {args.base_url}")
    
    results = {
        "test_timestamp": time.time(),
        "system_metrics_before": tester.get_system_metrics()
    }
    
    # Run individual test suites based on arguments
    print("\n1. Testing API endpoints...")
    results["api_endpoints"] = tester.test_api_endpoints(num_requests=args.api_requests)
    
    print("\n2. Testing database performance...")
    results["database_performance"] = tester.test_database_performance(num_queries=args.db_queries)
    
    print("\n3. Testing Redis performance...")
    results["redis_performance"] = tester.test_redis_performance(num_operations=args.redis_ops)
    
    print("\n4. Testing concurrent load...")
    results["concurrent_load"] = tester.test_concurrent_load(
        num_threads=args.threads, 
        requests_per_thread=args.requests_per_thread
    )
    
    results["system_metrics_after"] = tester.get_system_metrics()
    
    # Print summary
    tester.print_summary(results)
    
    # Save results
    if args.output:
        tester.save_results(results, args.output)
    else:
        tester.save_results(results)


if __name__ == "__main__":
    main()