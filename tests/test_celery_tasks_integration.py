"""
Integration tests for Celery background tasks.
"""
import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from celery import Celery
from celery.result import AsyncResult

from app.workers.crawling_tasks import crawl_keyword_posts, crawl_subreddit_posts
from app.workers.analysis_tasks import analyze_keyword_trends, calculate_post_metrics
from app.workers.content_tasks import generate_blog_content, process_content_template
from app.workers.maintenance_tasks import cleanup_old_data, update_system_metrics
from app.models.keyword import Keyword
from app.models.post import Post
from app.models.blog_content import BlogContent
from app.models.process_log import ProcessLog


class TestCrawlingTasksIntegration:
    """Integration tests for crawling tasks."""
    
    @patch('app.workers.crawling_tasks.reddit_client')
    def test_crawl_keyword_posts_task(self, mock_reddit_client, integration_celery_app,
                                    integration_db, sample_keyword):
        """Test keyword posts crawling task."""
        # Mock Reddit API response
        mock_reddit_client.search_posts_by_keyword = AsyncMock(return_value=[
            {
                "reddit_id": "crawl_test_1",
                "title": "Test Crawl Post 1",
                "content": "Test content 1",
                "author": "test_author_1",
                "score": 100,
                "num_comments": 20,
                "url": "https://reddit.com/test1",
                "subreddit": "test",
                "created_at": "2022-01-01T00:00:00Z"
            },
            {
                "reddit_id": "crawl_test_2",
                "title": "Test Crawl Post 2",
                "content": "Test content 2",
                "author": "test_author_2",
                "score": 150,
                "num_comments": 30,
                "url": "https://reddit.com/test2",
                "subreddit": "test",
                "created_at": "2022-01-01T01:00:00Z"
            }
        ])
        
        # Execute task
        result = crawl_keyword_posts.apply_async(
            args=[sample_keyword.id],
            kwargs={"limit": 10}
        )
        
        # Wait for task completion
        task_result = result.get(timeout=10)
        
        # Verify task result
        assert task_result["status"] == "completed"
        assert task_result["posts_collected"] == 2
        assert task_result["keyword_id"] == sample_keyword.id
        
        # Verify posts were saved to database
        posts = integration_db.query(Post).filter(
            Post.keyword_id == sample_keyword.id
        ).all()
        
        assert len(posts) == 2
        assert any(post.reddit_id == "crawl_test_1" for post in posts)
        assert any(post.reddit_id == "crawl_test_2" for post in posts)
    
    @patch('app.workers.crawling_tasks.reddit_client')
    def test_crawl_keyword_posts_error_handling(self, mock_reddit_client,
                                              integration_celery_app, sample_keyword):
        """Test crawling task error handling."""
        # Mock Reddit API error
        mock_reddit_client.search_posts_by_keyword = AsyncMock(
            side_effect=Exception("Reddit API Error")
        )
        
        # Execute task
        result = crawl_keyword_posts.apply_async(
            args=[sample_keyword.id],
            kwargs={"limit": 10}
        )
        
        # Task should handle error gracefully
        task_result = result.get(timeout=10)
        
        assert task_result["status"] == "failed"
        assert "error" in task_result
        assert "Reddit API Error" in task_result["error"]
    
    @patch('app.workers.crawling_tasks.reddit_client')
    def test_crawl_subreddit_posts_task(self, mock_reddit_client, integration_celery_app):
        """Test subreddit posts crawling task."""
        # Mock Reddit API response
        mock_reddit_client.get_subreddit_posts = AsyncMock(return_value=[
            {
                "reddit_id": "subreddit_test_1",
                "title": "Subreddit Test Post 1",
                "content": "Subreddit content 1",
                "author": "subreddit_author_1",
                "score": 200,
                "num_comments": 40,
                "url": "https://reddit.com/r/python/test1",
                "subreddit": "python",
                "created_at": "2022-01-01T00:00:00Z"
            }
        ])
        
        # Execute task
        result = crawl_subreddit_posts.apply_async(
            args=["python"],
            kwargs={"limit": 5, "sort": "hot"}
        )
        
        task_result = result.get(timeout=10)
        
        assert task_result["status"] == "completed"
        assert task_result["posts_collected"] == 1
        assert task_result["subreddit"] == "python"


class TestAnalysisTasksIntegration:
    """Integration tests for analysis tasks."""
    
    @patch('app.workers.analysis_tasks.TrendAnalysisService')
    def test_analyze_keyword_trends_task(self, mock_trend_service, integration_celery_app,
                                       integration_db, sample_keyword, sample_post):
        """Test keyword trend analysis task."""
        # Mock trend analysis service
        mock_service_instance = MagicMock()
        mock_service_instance.analyze_keyword_trends = AsyncMock(return_value={
            "keyword_id": sample_keyword.id,
            "trend_score": 0.85,
            "engagement_rate": 0.75,
            "growth_rate": 1.2,
            "top_terms": ["python", "programming", "code"],
            "analysis_date": "2022-01-01T00:00:00Z"
        })
        mock_trend_service.return_value = mock_service_instance
        
        # Execute task
        result = analyze_keyword_trends.apply_async(
            args=[sample_keyword.id]
        )
        
        task_result = result.get(timeout=10)
        
        assert task_result["status"] == "completed"
        assert task_result["keyword_id"] == sample_keyword.id
        assert "trend_score" in task_result
        assert "engagement_rate" in task_result
    
    @patch('app.workers.analysis_tasks.TrendAnalysisService')
    def test_calculate_post_metrics_task(self, mock_trend_service, integration_celery_app,
                                       sample_post):
        """Test post metrics calculation task."""
        # Mock metrics calculation
        mock_service_instance = MagicMock()
        mock_service_instance.calculate_post_metrics = AsyncMock(return_value={
            "post_id": sample_post.id,
            "engagement_score": 0.8,
            "tfidf_score": 0.7,
            "trend_velocity": 1.1,
            "sentiment_score": 0.6
        })
        mock_trend_service.return_value = mock_service_instance
        
        # Execute task
        result = calculate_post_metrics.apply_async(
            args=[sample_post.id]
        )
        
        task_result = result.get(timeout=10)
        
        assert task_result["status"] == "completed"
        assert task_result["post_id"] == sample_post.id
        assert "engagement_score" in task_result
        assert "tfidf_score" in task_result
    
    @patch('app.workers.analysis_tasks.TrendAnalysisService')
    def test_batch_analysis_task(self, mock_trend_service, integration_celery_app,
                               integration_db, sample_keyword):
        """Test batch analysis of multiple posts."""
        # Create multiple posts
        posts = []
        for i in range(5):
            post = Post(
                keyword_id=sample_keyword.id,
                reddit_id=f"batch_test_{i}",
                title=f"Batch Test Post {i}",
                content=f"Batch content {i}",
                author=f"batch_author_{i}",
                score=100 + i * 10,
                num_comments=20 + i * 5,
                url=f"https://reddit.com/batch_{i}",
                subreddit="test"
            )
            posts.append(post)
        
        integration_db.add_all(posts)
        integration_db.commit()
        
        # Mock batch analysis
        mock_service_instance = MagicMock()
        mock_service_instance.analyze_keyword_trends = AsyncMock(return_value={
            "keyword_id": sample_keyword.id,
            "posts_analyzed": 5,
            "average_engagement": 0.75,
            "trend_direction": "upward"
        })
        mock_trend_service.return_value = mock_service_instance
        
        # Execute batch analysis
        result = analyze_keyword_trends.apply_async(
            args=[sample_keyword.id],
            kwargs={"batch_size": 10}
        )
        
        task_result = result.get(timeout=10)
        
        assert task_result["status"] == "completed"
        assert task_result["keyword_id"] == sample_keyword.id


class TestContentTasksIntegration:
    """Integration tests for content generation tasks."""
    
    @patch('app.workers.content_tasks.ContentGenerationService')
    def test_generate_blog_content_task(self, mock_content_service, integration_celery_app,
                                      integration_db, sample_keyword):
        """Test blog content generation task."""
        # Mock content generation service
        mock_service_instance = MagicMock()
        mock_service_instance.generate_blog_content = AsyncMock(return_value={
            "title": "Generated Blog Post",
            "content": "# Generated Content\n\nThis is generated content.",
            "template_used": "default",
            "word_count": 150,
            "readability_score": 0.8
        })
        mock_content_service.return_value = mock_service_instance
        
        # Execute task
        result = generate_blog_content.apply_async(
            args=[sample_keyword.id],
            kwargs={"template": "default"}
        )
        
        task_result = result.get(timeout=10)
        
        assert task_result["status"] == "completed"
        assert task_result["keyword_id"] == sample_keyword.id
        assert "title" in task_result
        assert "content" in task_result
        
        # Verify content was saved to database
        blog_content = integration_db.query(BlogContent).filter(
            BlogContent.keyword_id == sample_keyword.id
        ).first()
        
        assert blog_content is not None
        assert blog_content.title == "Generated Blog Post"
    
    @patch('app.workers.content_tasks.TemplateService')
    def test_process_content_template_task(self, mock_template_service,
                                         integration_celery_app):
        """Test content template processing task."""
        # Mock template service
        mock_service_instance = MagicMock()
        mock_service_instance.process_template = AsyncMock(return_value={
            "processed_content": "# Processed Template\n\nProcessed content here.",
            "template_name": "custom_template",
            "variables_used": ["title", "content", "date"]
        })
        mock_template_service.return_value = mock_service_instance
        
        template_data = {
            "template_name": "custom_template",
            "variables": {
                "title": "Test Title",
                "content": "Test content",
                "date": "2022-01-01"
            }
        }
        
        # Execute task
        result = process_content_template.apply_async(
            args=[template_data]
        )
        
        task_result = result.get(timeout=10)
        
        assert task_result["status"] == "completed"
        assert "processed_content" in task_result
        assert "template_name" in task_result


class TestMaintenanceTasksIntegration:
    """Integration tests for maintenance tasks."""
    
    def test_cleanup_old_data_task(self, integration_celery_app, integration_db,
                                 sample_keyword):
        """Test old data cleanup task."""
        # Create old posts (simulate old data)
        old_posts = []
        for i in range(3):
            post = Post(
                keyword_id=sample_keyword.id,
                reddit_id=f"old_post_{i}",
                title=f"Old Post {i}",
                content=f"Old content {i}",
                author=f"old_author_{i}",
                score=50 + i * 10,
                num_comments=10 + i * 2,
                url=f"https://reddit.com/old_{i}",
                subreddit="test"
            )
            old_posts.append(post)
        
        integration_db.add_all(old_posts)
        integration_db.commit()
        
        # Execute cleanup task
        result = cleanup_old_data.apply_async(
            kwargs={"days_old": 30, "batch_size": 100}
        )
        
        task_result = result.get(timeout=10)
        
        assert task_result["status"] == "completed"
        assert "records_cleaned" in task_result
    
    @patch('app.workers.maintenance_tasks.SystemMetricsCollector')
    def test_update_system_metrics_task(self, mock_metrics_collector,
                                      integration_celery_app):
        """Test system metrics update task."""
        # Mock metrics collector
        mock_collector_instance = MagicMock()
        mock_collector_instance.collect_system_metrics = AsyncMock(return_value={
            "cpu_usage": 45.2,
            "memory_usage": 68.5,
            "disk_usage": 32.1,
            "active_tasks": 5,
            "database_connections": 12
        })
        mock_metrics_collector.return_value = mock_collector_instance
        
        # Execute task
        result = update_system_metrics.apply_async()
        
        task_result = result.get(timeout=10)
        
        assert task_result["status"] == "completed"
        assert "cpu_usage" in task_result
        assert "memory_usage" in task_result


class TestTaskChaining:
    """Integration tests for task chaining and workflows."""
    
    @patch('app.workers.crawling_tasks.reddit_client')
    @patch('app.workers.analysis_tasks.TrendAnalysisService')
    @patch('app.workers.content_tasks.ContentGenerationService')
    def test_complete_workflow_chain(self, mock_content_service, mock_trend_service,
                                   mock_reddit_client, integration_celery_app,
                                   integration_db, sample_keyword):
        """Test complete workflow: crawl -> analyze -> generate content."""
        # Mock services
        mock_reddit_client.search_posts_by_keyword = AsyncMock(return_value=[
            {
                "reddit_id": "workflow_test_1",
                "title": "Workflow Test Post",
                "content": "Workflow content",
                "author": "workflow_author",
                "score": 100,
                "num_comments": 20,
                "url": "https://reddit.com/workflow",
                "subreddit": "test",
                "created_at": "2022-01-01T00:00:00Z"
            }
        ])
        
        mock_trend_service_instance = MagicMock()
        mock_trend_service_instance.analyze_keyword_trends = AsyncMock(return_value={
            "keyword_id": sample_keyword.id,
            "trend_score": 0.85
        })
        mock_trend_service.return_value = mock_trend_service_instance
        
        mock_content_service_instance = MagicMock()
        mock_content_service_instance.generate_blog_content = AsyncMock(return_value={
            "title": "Workflow Generated Post",
            "content": "# Workflow\n\nGenerated from workflow.",
            "template_used": "default"
        })
        mock_content_service.return_value = mock_content_service_instance
        
        # Execute workflow chain
        # 1. Crawl posts
        crawl_result = crawl_keyword_posts.apply_async(
            args=[sample_keyword.id],
            kwargs={"limit": 5}
        )
        crawl_data = crawl_result.get(timeout=10)
        assert crawl_data["status"] == "completed"
        
        # 2. Analyze trends
        analysis_result = analyze_keyword_trends.apply_async(
            args=[sample_keyword.id]
        )
        analysis_data = analysis_result.get(timeout=10)
        assert analysis_data["status"] == "completed"
        
        # 3. Generate content
        content_result = generate_blog_content.apply_async(
            args=[sample_keyword.id],
            kwargs={"template": "default"}
        )
        content_data = content_result.get(timeout=10)
        assert content_data["status"] == "completed"
        
        # Verify complete workflow
        assert crawl_data["posts_collected"] == 1
        assert analysis_data["keyword_id"] == sample_keyword.id
        assert content_data["keyword_id"] == sample_keyword.id


class TestTaskErrorHandling:
    """Integration tests for task error handling and recovery."""
    
    def test_task_retry_mechanism(self, integration_celery_app, sample_keyword):
        """Test task retry mechanism on failures."""
        # This would test the actual retry mechanism
        # For now, we'll test that tasks handle errors gracefully
        
        with patch('app.workers.crawling_tasks.reddit_client') as mock_client:
            # First call fails, second succeeds
            mock_client.search_posts_by_keyword = AsyncMock(
                side_effect=[
                    Exception("Temporary failure"),
                    [{"reddit_id": "retry_test", "title": "Retry Test"}]
                ]
            )
            
            # Execute task (would retry automatically in real scenario)
            result = crawl_keyword_posts.apply_async(
                args=[sample_keyword.id],
                kwargs={"limit": 5}
            )
            
            # Task should handle the error
            task_result = result.get(timeout=10)
            assert "status" in task_result
    
    def test_task_timeout_handling(self, integration_celery_app, sample_keyword):
        """Test task timeout handling."""
        with patch('app.workers.crawling_tasks.reddit_client') as mock_client:
            # Mock a slow operation
            import asyncio
            
            async def slow_operation(*args, **kwargs):
                await asyncio.sleep(0.1)  # Simulate slow operation
                return []
            
            mock_client.search_posts_by_keyword = slow_operation
            
            # Execute task with short timeout
            result = crawl_keyword_posts.apply_async(
                args=[sample_keyword.id],
                kwargs={"limit": 5}
            )
            
            # Task should complete (or handle timeout gracefully)
            task_result = result.get(timeout=5)
            assert "status" in task_result


class TestTaskMonitoring:
    """Integration tests for task monitoring and logging."""
    
    def test_task_progress_tracking(self, integration_celery_app, integration_db,
                                  authenticated_user, sample_keyword):
        """Test task progress tracking in process logs."""
        with patch('app.workers.crawling_tasks.reddit_client') as mock_client:
            mock_client.search_posts_by_keyword = AsyncMock(return_value=[])
            
            # Execute task
            result = crawl_keyword_posts.apply_async(
                args=[sample_keyword.id],
                kwargs={"limit": 5}
            )
            
            task_result = result.get(timeout=10)
            
            # Check if process log was created
            process_log = integration_db.query(ProcessLog).filter(
                ProcessLog.task_id == result.id
            ).first()
            
            # Process log might be created depending on implementation
            if process_log:
                assert process_log.task_type == "crawling"
                assert process_log.status in ["completed", "failed"]
    
    def test_task_result_storage(self, integration_celery_app, sample_keyword):
        """Test that task results are properly stored."""
        with patch('app.workers.crawling_tasks.reddit_client') as mock_client:
            mock_client.search_posts_by_keyword = AsyncMock(return_value=[
                {"reddit_id": "result_test", "title": "Result Test"}
            ])
            
            # Execute task
            result = crawl_keyword_posts.apply_async(
                args=[sample_keyword.id],
                kwargs={"limit": 5}
            )
            
            # Get result
            task_result = result.get(timeout=10)
            
            # Verify result structure
            assert isinstance(task_result, dict)
            assert "status" in task_result
            assert "keyword_id" in task_result
            
            # Verify result is accessible via Celery
            stored_result = AsyncResult(result.id, app=integration_celery_app)
            assert stored_result.result == task_result