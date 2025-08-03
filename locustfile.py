"""
Locust load testing script for Reddit Content Platform API.
"""

import json
import random
import time
from typing import Dict, Any, List

from locust import HttpUser, task, between, events
from locust.exception import RescheduleTask


class RedditPlatformUser(HttpUser):
    """Simulated user for load testing the Reddit Content Platform."""
    
    wait_time = between(1, 5)  # Wait 1-5 seconds between requests
    
    def on_start(self):
        """Initialize user session."""
        self.auth_token = None
        self.user_id = None
        self.keywords = []
        self.posts = []
        
        # Authenticate user
        self.authenticate()
    
    def authenticate(self):
        """Authenticate user and get JWT token."""
        # For load testing, we'll use a mock authentication
        # In real scenario, this would use OAuth2 flow
        auth_data = {
            "username": f"testuser_{random.randint(1, 1000)}",
            "password": "testpassword"
        }
        
        try:
            response = self.client.post("/api/v1/auth/login", json=auth_data)
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data.get("access_token")
                self.user_id = data.get("user_id")
                
                # Set authorization header for subsequent requests
                self.client.headers.update({
                    "Authorization": f"Bearer {self.auth_token}"
                })
            else:
                # For load testing, continue without auth if login fails
                self.auth_token = "mock_token"
                self.user_id = random.randint(1, 100)
                
        except Exception as e:
            # Mock authentication for load testing
            self.auth_token = "mock_token"
            self.user_id = random.randint(1, 100)
    
    @task(3)
    def get_posts(self):
        """Test getting posts with various parameters."""
        params = {
            "page": random.randint(1, 5),
            "per_page": random.choice([10, 20, 50]),
            "sort_by": random.choice(["created_at", "score", "num_comments"]),
            "sort_order": random.choice(["asc", "desc"])
        }
        
        # Add optional filters randomly
        if random.random() < 0.3:  # 30% chance to add filters
            params["min_score"] = random.randint(1, 10)
        
        if random.random() < 0.2:  # 20% chance to add search
            params["search"] = random.choice([
                "python", "javascript", "react", "api", "database"
            ])
        
        with self.client.get(
            "/api/v1/posts", 
            params=params,
            catch_response=True
        ) as response:
            if response.status_code == 200:
                data = response.json()
                self.posts = data.get("posts", [])
                response.success()
            else:
                response.failure(f"Got status code {response.status_code}")
    
    @task(2)
    def get_keywords(self):
        """Test getting user keywords."""
        params = {
            "skip": 0,
            "limit": random.choice([10, 20, 50]),
            "active_only": random.choice([True, False])
        }
        
        with self.client.get(
            "/api/v1/keywords",
            params=params,
            catch_response=True
        ) as response:
            if response.status_code == 200:
                data = response.json()
                self.keywords = data.get("keywords", [])
                response.success()
            else:
                response.failure(f"Got status code {response.status_code}")
    
    @task(2)
    def get_trends(self):
        """Test getting trend analysis data."""
        if not self.keywords:
            # Skip if no keywords available
            raise RescheduleTask()
        
        keyword_id = random.choice(self.keywords).get("id") if self.keywords else 1
        
        with self.client.get(
            f"/api/v1/trends/keyword/{keyword_id}",
            catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Got status code {response.status_code}")
    
    @task(1)
    def get_post_detail(self):
        """Test getting individual post details."""
        if not self.posts:
            # Skip if no posts available
            raise RescheduleTask()
        
        post_id = random.choice(self.posts).get("id") if self.posts else 1
        
        with self.client.get(
            f"/api/v1/posts/{post_id}",
            catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
            elif response.status_code == 404:
                # 404 is acceptable for non-existent posts
                response.success()
            else:
                response.failure(f"Got status code {response.status_code}")
    
    @task(1)
    def create_keyword(self):
        """Test creating new keywords."""
        keyword_data = {
            "keyword": f"test_keyword_{random.randint(1, 10000)}",
            "is_active": True
        }
        
        with self.client.post(
            "/api/v1/keywords",
            json=keyword_data,
            catch_response=True
        ) as response:
            if response.status_code in [200, 201]:
                response.success()
            elif response.status_code == 409:
                # Conflict is acceptable for duplicate keywords
                response.success()
            else:
                response.failure(f"Got status code {response.status_code}")
    
    @task(1)
    def get_health_check(self):
        """Test health check endpoint."""
        with self.client.get("/health", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Got status code {response.status_code}")
    
    @task(1)
    def get_public_blog_posts(self):
        """Test public blog posts endpoint."""
        params = {
            "page": random.randint(1, 3),
            "per_page": random.choice([10, 20]),
            "category": random.choice(["tech", "news", "analysis", None])
        }
        
        # Remove None values
        params = {k: v for k, v in params.items() if v is not None}
        
        with self.client.get(
            "/api/v1/public-blog/posts",
            params=params,
            catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Got status code {response.status_code}")


class AdminUser(HttpUser):
    """Simulated admin user for testing admin-specific endpoints."""
    
    wait_time = between(2, 8)  # Longer wait time for admin operations
    weight = 1  # Lower weight compared to regular users
    
    def on_start(self):
        """Initialize admin session."""
        self.auth_token = "admin_mock_token"
        self.client.headers.update({
            "Authorization": f"Bearer {self.auth_token}"
        })
    
    @task(2)
    def start_crawling_task(self):
        """Test starting crawling tasks."""
        crawl_data = {
            "keyword_ids": [random.randint(1, 10) for _ in range(random.randint(1, 3))],
            "priority": random.choice(["low", "normal", "high"])
        }
        
        with self.client.post(
            "/api/v1/crawling/start",
            json=crawl_data,
            catch_response=True
        ) as response:
            if response.status_code in [200, 202]:
                response.success()
            else:
                response.failure(f"Got status code {response.status_code}")
    
    @task(1)
    def get_crawling_status(self):
        """Test getting crawling status."""
        task_id = f"mock_task_{random.randint(1, 100)}"
        
        with self.client.get(
            f"/api/v1/crawling/status/{task_id}",
            catch_response=True
        ) as response:
            if response.status_code in [200, 404]:
                response.success()
            else:
                response.failure(f"Got status code {response.status_code}")
    
    @task(1)
    def generate_content(self):
        """Test content generation."""
        content_data = {
            "keyword_id": random.randint(1, 10),
            "template_type": random.choice(["default", "listicle", "news"])
        }
        
        with self.client.post(
            "/api/v1/content/generate",
            json=content_data,
            catch_response=True
        ) as response:
            if response.status_code in [200, 202]:
                response.success()
            else:
                response.failure(f"Got status code {response.status_code}")


class HighVolumeUser(HttpUser):
    """High-volume user for stress testing."""
    
    wait_time = between(0.1, 0.5)  # Very short wait time
    weight = 2  # Higher weight for stress testing
    
    def on_start(self):
        self.auth_token = "high_volume_mock_token"
        self.client.headers.update({
            "Authorization": f"Bearer {self.auth_token}"
        })
    
    @task(5)
    def rapid_posts_requests(self):
        """Rapid-fire posts requests."""
        params = {
            "page": random.randint(1, 2),
            "per_page": 10
        }
        
        with self.client.get("/api/v1/posts", params=params, catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Got status code {response.status_code}")
    
    @task(3)
    def rapid_health_checks(self):
        """Rapid health check requests."""
        with self.client.get("/health", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Got status code {response.status_code}")


# Custom events for detailed monitoring
@events.request.add_listener
def on_request(request_type, name, response_time, response_length, exception, context, **kwargs):
    """Log detailed request information."""
    if exception:
        print(f"Request failed: {request_type} {name} - {exception}")
    elif response_time > 2000:  # Log slow requests (>2s)
        print(f"Slow request: {request_type} {name} - {response_time}ms")


@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """Initialize test environment."""
    print("Load test starting...")
    print(f"Target host: {environment.host}")


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """Clean up after test."""
    print("Load test completed.")
    
    # Print summary statistics
    stats = environment.stats
    print(f"Total requests: {stats.total.num_requests}")
    print(f"Total failures: {stats.total.num_failures}")
    print(f"Average response time: {stats.total.avg_response_time:.2f}ms")
    print(f"Max response time: {stats.total.max_response_time:.2f}ms")


# Load test scenarios
class LightLoadTest(HttpUser):
    """Light load test scenario."""
    tasks = [RedditPlatformUser]
    min_wait = 2000
    max_wait = 5000


class MediumLoadTest(HttpUser):
    """Medium load test scenario."""
    tasks = [RedditPlatformUser, AdminUser]
    min_wait = 1000
    max_wait = 3000


class HeavyLoadTest(HttpUser):
    """Heavy load test scenario."""
    tasks = [RedditPlatformUser, AdminUser, HighVolumeUser]
    min_wait = 100
    max_wait = 1000


# Custom load test shapes
from locust import LoadTestShape

class StepLoadShape(LoadTestShape):
    """Step load testing shape."""
    
    step_time = 30  # 30 seconds per step
    step_load = 10  # 10 users per step
    spawn_rate = 2  # 2 users per second
    time_limit = 300  # 5 minutes total
    
    def tick(self):
        run_time = self.get_run_time()
        
        if run_time > self.time_limit:
            return None
        
        current_step = run_time // self.step_time
        return (current_step * self.step_load, self.spawn_rate)


class SpikeLoadShape(LoadTestShape):
    """Spike load testing shape."""
    
    def tick(self):
        run_time = self.get_run_time()
        
        if run_time < 60:
            # Ramp up to 50 users
            return (50, 2)
        elif run_time < 120:
            # Spike to 200 users
            return (200, 10)
        elif run_time < 180:
            # Drop back to 50 users
            return (50, 5)
        elif run_time < 240:
            # Final spike to 300 users
            return (300, 15)
        else:
            return None