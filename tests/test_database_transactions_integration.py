"""
Integration tests for database transactions and data consistency.
"""
import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from app.models.user import User
from app.models.keyword import Keyword
from app.models.post import Post
from app.models.blog_content import BlogContent
from app.models.metric import Metric
from app.models.process_log import ProcessLog


class TestUserTransactions:
    """Test user-related database transactions."""
    
    def test_user_creation_and_retrieval(self, integration_db):
        """Test user creation and retrieval."""
        user_data = {
            "name": "Test User",
            "email": "test@example.com",
            "oauth_provider": "reddit"
        }
        
        # Create user
        user = User(**user_data)
        integration_db.add(user)
        integration_db.commit()
        integration_db.refresh(user)
        
        assert user.id is not None
        assert user.created_at is not None
        assert user.updated_at is not None
        
        # Retrieve user
        retrieved_user = integration_db.query(User).filter(
            User.email == "test@example.com"
        ).first()
        
        assert retrieved_user is not None
        assert retrieved_user.name == "Test User"
        assert retrieved_user.oauth_provider == "reddit"
    
    def test_user_email_uniqueness(self, integration_db):
        """Test that user email must be unique."""
        user1 = User(
            name="User 1",
            email="duplicate@example.com",
            oauth_provider="reddit"
        )
        integration_db.add(user1)
        integration_db.commit()
        
        # Try to create another user with same email
        user2 = User(
            name="User 2",
            email="duplicate@example.com",
            oauth_provider="reddit"
        )
        integration_db.add(user2)
        
        with pytest.raises(IntegrityError):
            integration_db.commit()
        
        integration_db.rollback()


class TestKeywordTransactions:
    """Test keyword-related database transactions."""
    
    def test_keyword_user_relationship(self, integration_db, authenticated_user):
        """Test keyword-user relationship and cascading."""
        # Create keyword
        keyword = Keyword(
            user_id=authenticated_user.id,
            keyword="test keyword",
            is_active=True
        )
        integration_db.add(keyword)
        integration_db.commit()
        integration_db.refresh(keyword)
        
        # Verify relationship
        assert keyword.user_id == authenticated_user.id
        
        # Test cascade delete (if implemented)
        keyword_id = keyword.id
        integration_db.delete(authenticated_user)
        integration_db.commit()
        
        # Keyword should be deleted or user_id should be null
        remaining_keyword = integration_db.query(Keyword).filter(
            Keyword.id == keyword_id
        ).first()
        
        # Depending on cascade settings, keyword might be deleted or orphaned
        if remaining_keyword:
            assert remaining_keyword.user_id is None
    
    def test_keyword_uniqueness_per_user(self, integration_db, authenticated_user):
        """Test that keywords are unique per user."""
        # Create first keyword
        keyword1 = Keyword(
            user_id=authenticated_user.id,
            keyword="python",
            is_active=True
        )
        integration_db.add(keyword1)
        integration_db.commit()
        
        # Try to create duplicate keyword for same user
        keyword2 = Keyword(
            user_id=authenticated_user.id,
            keyword="python",
            is_active=True
        )
        integration_db.add(keyword2)
        
        with pytest.raises(IntegrityError):
            integration_db.commit()
        
        integration_db.rollback()
    
    def test_keyword_soft_delete(self, integration_db, sample_keyword):
        """Test keyword soft delete by setting is_active to False."""
        # Verify keyword is active
        assert sample_keyword.is_active is True
        
        # Soft delete
        sample_keyword.is_active = False
        integration_db.commit()
        
        # Verify soft delete
        updated_keyword = integration_db.query(Keyword).filter(
            Keyword.id == sample_keyword.id
        ).first()
        
        assert updated_keyword is not None
        assert updated_keyword.is_active is False


class TestPostTransactions:
    """Test post-related database transactions."""
    
    def test_post_keyword_relationship(self, integration_db, sample_keyword):
        """Test post-keyword relationship."""
        post_data = {
            "keyword_id": sample_keyword.id,
            "reddit_id": "test_post_123",
            "title": "Test Post",
            "content": "Test content",
            "author": "test_author",
            "score": 100,
            "num_comments": 10,
            "url": "https://reddit.com/test",
            "subreddit": "test"
        }
        
        post = Post(**post_data)
        integration_db.add(post)
        integration_db.commit()
        integration_db.refresh(post)
        
        # Verify relationship
        assert post.keyword_id == sample_keyword.id
        
        # Test foreign key constraint
        invalid_post = Post(
            keyword_id=99999,  # Non-existent keyword
            reddit_id="invalid_post",
            title="Invalid Post",
            content="Invalid content",
            author="invalid_author",
            score=0,
            num_comments=0,
            url="https://reddit.com/invalid",
            subreddit="invalid"
        )
        integration_db.add(invalid_post)
        
        with pytest.raises(IntegrityError):
            integration_db.commit()
        
        integration_db.rollback()
    
    def test_post_reddit_id_uniqueness(self, integration_db, sample_keyword):
        """Test that reddit_id must be unique."""
        post1 = Post(
            keyword_id=sample_keyword.id,
            reddit_id="duplicate_reddit_id",
            title="Post 1",
            content="Content 1",
            author="author1",
            score=100,
            num_comments=10,
            url="https://reddit.com/post1",
            subreddit="test"
        )
        integration_db.add(post1)
        integration_db.commit()
        
        # Try to create another post with same reddit_id
        post2 = Post(
            keyword_id=sample_keyword.id,
            reddit_id="duplicate_reddit_id",
            title="Post 2",
            content="Content 2",
            author="author2",
            score=200,
            num_comments=20,
            url="https://reddit.com/post2",
            subreddit="test"
        )
        integration_db.add(post2)
        
        with pytest.raises(IntegrityError):
            integration_db.commit()
        
        integration_db.rollback()
    
    def test_bulk_post_insertion(self, integration_db, sample_keyword):
        """Test bulk insertion of posts."""
        posts = []
        for i in range(10):
            post = Post(
                keyword_id=sample_keyword.id,
                reddit_id=f"bulk_post_{i}",
                title=f"Bulk Post {i}",
                content=f"Bulk content {i}",
                author=f"author_{i}",
                score=i * 10,
                num_comments=i * 2,
                url=f"https://reddit.com/bulk_{i}",
                subreddit="test"
            )
            posts.append(post)
        
        # Bulk insert
        integration_db.add_all(posts)
        integration_db.commit()
        
        # Verify all posts were inserted
        count = integration_db.query(Post).filter(
            Post.keyword_id == sample_keyword.id
        ).count()
        
        assert count >= 10


class TestBlogContentTransactions:
    """Test blog content-related database transactions."""
    
    def test_blog_content_creation(self, integration_db, sample_keyword):
        """Test blog content creation and retrieval."""
        blog_content = BlogContent(
            keyword_id=sample_keyword.id,
            title="Test Blog Post",
            content="# Test Blog\n\nThis is test content.",
            template_used="default",
            status="draft"
        )
        
        integration_db.add(blog_content)
        integration_db.commit()
        integration_db.refresh(blog_content)
        
        assert blog_content.id is not None
        assert blog_content.created_at is not None
        assert blog_content.updated_at is not None
        
        # Test status update
        blog_content.status = "published"
        integration_db.commit()
        
        updated_content = integration_db.query(BlogContent).filter(
            BlogContent.id == blog_content.id
        ).first()
        
        assert updated_content.status == "published"
        assert updated_content.updated_at > updated_content.created_at


class TestMetricTransactions:
    """Test metric-related database transactions."""
    
    def test_metric_post_relationship(self, integration_db, sample_post):
        """Test metric-post relationship."""
        metric = Metric(
            post_id=sample_post.id,
            engagement_score=0.85,
            tfidf_score=0.75,
            trend_velocity=1.2
        )
        
        integration_db.add(metric)
        integration_db.commit()
        integration_db.refresh(metric)
        
        assert metric.post_id == sample_post.id
        assert metric.calculated_at is not None
    
    def test_metric_calculations_update(self, integration_db, sample_post):
        """Test updating metric calculations."""
        # Create initial metric
        metric = Metric(
            post_id=sample_post.id,
            engagement_score=0.5,
            tfidf_score=0.4,
            trend_velocity=0.8
        )
        integration_db.add(metric)
        integration_db.commit()
        
        original_calculated_at = metric.calculated_at
        
        # Update metrics
        metric.engagement_score = 0.9
        metric.tfidf_score = 0.8
        metric.trend_velocity = 1.5
        integration_db.commit()
        
        # Verify updates
        updated_metric = integration_db.query(Metric).filter(
            Metric.id == metric.id
        ).first()
        
        assert updated_metric.engagement_score == 0.9
        assert updated_metric.tfidf_score == 0.8
        assert updated_metric.trend_velocity == 1.5


class TestProcessLogTransactions:
    """Test process log-related database transactions."""
    
    def test_process_log_lifecycle(self, integration_db, authenticated_user):
        """Test complete process log lifecycle."""
        # Create process log
        process_log = ProcessLog(
            user_id=authenticated_user.id,
            task_type="crawling",
            status="pending",
            task_id="test-task-123"
        )
        
        integration_db.add(process_log)
        integration_db.commit()
        integration_db.refresh(process_log)
        
        assert process_log.id is not None
        assert process_log.created_at is not None
        assert process_log.status == "pending"
        
        # Update to running
        process_log.status = "running"
        integration_db.commit()
        
        # Update to completed
        process_log.status = "completed"
        process_log.completed_at = datetime.now(timezone.utc)
        integration_db.commit()
        
        # Verify final state
        final_log = integration_db.query(ProcessLog).filter(
            ProcessLog.id == process_log.id
        ).first()
        
        assert final_log.status == "completed"
        assert final_log.completed_at is not None
    
    def test_process_log_error_handling(self, integration_db, authenticated_user):
        """Test process log error handling."""
        process_log = ProcessLog(
            user_id=authenticated_user.id,
            task_type="analysis",
            status="running",
            task_id="error-task-456"
        )
        
        integration_db.add(process_log)
        integration_db.commit()
        
        # Simulate error
        process_log.status = "failed"
        process_log.error_message = "Test error message"
        process_log.completed_at = datetime.now(timezone.utc)
        integration_db.commit()
        
        # Verify error state
        error_log = integration_db.query(ProcessLog).filter(
            ProcessLog.id == process_log.id
        ).first()
        
        assert error_log.status == "failed"
        assert error_log.error_message == "Test error message"
        assert error_log.completed_at is not None


class TestTransactionRollback:
    """Test transaction rollback scenarios."""
    
    def test_rollback_on_error(self, integration_db, authenticated_user):
        """Test that transactions rollback properly on errors."""
        # Start transaction
        keyword = Keyword(
            user_id=authenticated_user.id,
            keyword="rollback test",
            is_active=True
        )
        integration_db.add(keyword)
        integration_db.flush()  # Flush but don't commit
        
        keyword_id = keyword.id
        
        # Simulate error and rollback
        try:
            # Create invalid post (this should fail)
            invalid_post = Post(
                keyword_id=keyword_id,
                reddit_id=None,  # This should cause an error
                title="Invalid Post",
                content="Invalid content",
                author="invalid_author",
                score=0,
                num_comments=0,
                url="https://reddit.com/invalid",
                subreddit="invalid"
            )
            integration_db.add(invalid_post)
            integration_db.commit()
        except Exception:
            integration_db.rollback()
        
        # Verify that keyword was not saved due to rollback
        saved_keyword = integration_db.query(Keyword).filter(
            Keyword.keyword == "rollback test"
        ).first()
        
        assert saved_keyword is None


class TestConcurrentTransactions:
    """Test concurrent transaction scenarios."""
    
    def test_concurrent_keyword_creation(self, integration_db_session, authenticated_user):
        """Test concurrent keyword creation scenarios."""
        # Simulate two concurrent sessions
        session1 = integration_db_session()
        session2 = integration_db_session()
        
        try:
            # Both sessions try to create the same keyword
            keyword1 = Keyword(
                user_id=authenticated_user.id,
                keyword="concurrent test",
                is_active=True
            )
            keyword2 = Keyword(
                user_id=authenticated_user.id,
                keyword="concurrent test",
                is_active=True
            )
            
            session1.add(keyword1)
            session2.add(keyword2)
            
            # First commit should succeed
            session1.commit()
            
            # Second commit should fail due to uniqueness constraint
            with pytest.raises(IntegrityError):
                session2.commit()
            
        finally:
            session1.close()
            session2.close()


class TestDataConsistency:
    """Test data consistency across related tables."""
    
    def test_cascade_delete_consistency(self, integration_db, authenticated_user):
        """Test data consistency when deleting related records."""
        # Create keyword
        keyword = Keyword(
            user_id=authenticated_user.id,
            keyword="consistency test",
            is_active=True
        )
        integration_db.add(keyword)
        integration_db.commit()
        integration_db.refresh(keyword)
        
        # Create related post
        post = Post(
            keyword_id=keyword.id,
            reddit_id="consistency_post",
            title="Consistency Test Post",
            content="Test content",
            author="test_author",
            score=100,
            num_comments=10,
            url="https://reddit.com/consistency",
            subreddit="test"
        )
        integration_db.add(post)
        integration_db.commit()
        integration_db.refresh(post)
        
        # Create related metric
        metric = Metric(
            post_id=post.id,
            engagement_score=0.8,
            tfidf_score=0.7,
            trend_velocity=1.1
        )
        integration_db.add(metric)
        integration_db.commit()
        
        # Delete keyword
        integration_db.delete(keyword)
        integration_db.commit()
        
        # Verify related records are handled appropriately
        remaining_post = integration_db.query(Post).filter(
            Post.id == post.id
        ).first()
        
        remaining_metric = integration_db.query(Metric).filter(
            Metric.id == metric.id
        ).first()
        
        # Depending on cascade settings, related records might be deleted
        # or foreign keys might be set to null
        if remaining_post:
            assert remaining_post.keyword_id is None
        
        if remaining_metric and not remaining_post:
            # If post is deleted, metric should also be deleted
            assert remaining_metric is None