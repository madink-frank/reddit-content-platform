"""
Integration test for content generation functionality.
"""

import pytest
import asyncio
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.base import BaseModel
from app.models.user import User
from app.models.keyword import Keyword
from app.models.post import Post
from app.models.blog_content import BlogContent
from app.services.content_generation_service import ContentGenerationService
from app.schemas.blog_content import ContentGenerationRequest


# Create in-memory SQLite database for testing
engine = create_engine("sqlite:///:memory:", echo=False)
BaseModel.metadata.create_all(engine)
SessionLocal = sessionmaker(bind=engine)


def create_test_data():
    """Create test data for integration testing."""
    db = SessionLocal()
    
    try:
        # Create test user
        user = User(
            name="Test User",
            email="test@example.com",
            oauth_provider="reddit",
            oauth_id="test_oauth_id_123"
        )
        db.add(user)
        db.flush()
        
        # Create test keyword
        keyword = Keyword(
            user_id=user.id,
            keyword="python_programming",
            is_active=True
        )
        db.add(keyword)
        db.flush()
        
        # Store IDs before committing
        user_id = user.id
        keyword_id = keyword.id
        
        # Create test posts
        posts = [
            Post(
                keyword_id=keyword_id,
                reddit_id="post1",
                title="Best Python Libraries for 2024",
                content="Python has amazing libraries for data science, web development, and more.",
                author="pythondev",
                score=1500,
                num_comments=85,
                url="https://reddit.com/r/python/post1",
                subreddit="python",
                post_created_at=datetime.utcnow(),
                created_at=datetime.utcnow()
            ),
            Post(
                keyword_id=keyword_id,
                reddit_id="post2",
                title="Python vs JavaScript: Which to Learn First?",
                content="Both languages have their strengths. Python is great for beginners.",
                author="coder123",
                score=890,
                num_comments=42,
                url="https://reddit.com/r/programming/post2",
                subreddit="programming",
                post_created_at=datetime.utcnow(),
                created_at=datetime.utcnow()
            ),
            Post(
                keyword_id=keyword_id,
                reddit_id="post3",
                title="Machine Learning with Python Tutorial",
                content="Learn how to build ML models using scikit-learn and pandas.",
                author="mlexpert",
                score=2100,
                num_comments=156,
                url="https://reddit.com/r/MachineLearning/post3",
                subreddit="MachineLearning",
                post_created_at=datetime.utcnow(),
                created_at=datetime.utcnow()
            )
        ]
        
        for post in posts:
            db.add(post)
        
        db.commit()
        return user_id, keyword_id, len(posts)
        
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()


async def test_full_content_generation():
    """Test the complete content generation workflow."""
    print("Testing full content generation workflow...")
    
    # Create test data
    user_id, keyword_id, post_count = create_test_data()
    db = SessionLocal()
    
    # Get the keyword object
    keyword = db.query(Keyword).filter(Keyword.id == keyword_id).first()
    
    try:
        # Initialize content generation service
        content_service = ContentGenerationService()
        
        # Create generation request
        request = ContentGenerationRequest(
            keyword_id=keyword_id,
            template_type="default",
            include_trends=True,
            include_top_posts=True,
            max_posts=3,
            custom_prompt="This is a comprehensive analysis of Python programming discussions."
        )
        
        print(f"Generating content for keyword: {keyword.keyword}")
        
        # Generate content
        blog_content = await content_service.generate_blog_content(request, db)
        
        # Verify content was generated
        assert blog_content is not None
        assert blog_content.id is not None
        assert blog_content.keyword_id == keyword_id
        assert blog_content.title is not None
        assert len(blog_content.title) > 0
        assert blog_content.content is not None
        assert len(blog_content.content) > 100  # Should be substantial content
        assert blog_content.template_used == "default"
        assert blog_content.word_count > 0
        assert blog_content.slug is not None
        assert blog_content.status == "draft"
        
        print(f"✓ Generated blog content with ID: {blog_content.id}")
        print(f"✓ Title: {blog_content.title}")
        print(f"✓ Word count: {blog_content.word_count}")
        print(f"✓ Slug: {blog_content.slug}")
        
        # Test content preview
        preview = await content_service.preview_content(request, db)
        assert preview is not None
        assert "title" in preview
        assert "content_preview" in preview
        assert "word_count" in preview
        assert "tags" in preview
        
        print(f"✓ Generated preview with {preview['word_count']} words")
        
        # Verify content contains expected elements
        content_lower = blog_content.content.lower()
        assert "python" in content_lower
        assert "programming" in content_lower
        assert "reddit" in content_lower
        
        print("✓ Content contains expected keywords")
        
        # Test different templates
        for template_type in ["news", "listicle"]:
            new_request = ContentGenerationRequest(
                keyword_id=keyword_id,
                template_type=template_type,
                include_trends=True,
                include_top_posts=True,
                max_posts=3
            )
            template_content = await content_service.generate_blog_content(new_request, db)
            assert template_content is not None
            assert template_content.template_used == template_type
            print(f"✓ Generated content with {template_type} template")
        
        return True
        
    except Exception as e:
        print(f"❌ Content generation test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()


async def test_template_functionality():
    """Test template system functionality."""
    print("Testing template system...")
    
    from app.services.template_service import TemplateService
    
    template_service = TemplateService()
    
    # Test getting available templates
    templates = template_service.get_available_templates()
    assert len(templates) >= 3  # default, news, listicle
    
    template_names = [t["name"] for t in templates]
    assert "default" in template_names
    assert "news" in template_names
    assert "listicle" in template_names
    
    print(f"✓ Found {len(templates)} available templates")
    
    # Test custom template creation
    custom_template = """# {{ title }}

Custom template for {{ keyword }}.

{% if trend_data %}
Trend: {{ trend_data.trend_direction }}
{% endif %}

Generated: {{ generated_at }}
"""
    
    success = template_service.create_custom_template(
        "custom_test",
        custom_template,
        "Test custom template"
    )
    assert success
    
    # Test rendering custom template
    context = {
        "title": "Test Custom",
        "keyword": "test",
        "trend_data": {"trend_direction": "rising"}
    }
    
    rendered = template_service.render_template("custom_test", context)
    assert rendered is not None
    assert "Test Custom" in rendered
    assert "rising" in rendered
    
    print("✓ Custom template creation and rendering works")
    
    # Clean up custom template
    template_service.delete_template("custom_test")
    
    return True


async def main():
    """Run all integration tests."""
    print("Starting content generation integration tests...\n")
    
    try:
        # Test template functionality
        await test_template_functionality()
        print()
        
        # Test full content generation
        await test_full_content_generation()
        print()
        
        print("✅ All integration tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Integration tests failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)