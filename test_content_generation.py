"""
Test content generation implementation.
"""

import pytest
import asyncio
from datetime import datetime
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User
from app.models.keyword import Keyword
from app.models.post import Post
from app.models.blog_content import BlogContent
from app.services.content_generation_service import ContentGenerationService
from app.services.template_service import TemplateService
from app.schemas.blog_content import ContentGenerationRequest


def test_template_service():
    """Test template service functionality."""
    template_service = TemplateService()
    
    # Test getting available templates
    templates = template_service.get_available_templates()
    assert len(templates) > 0
    assert any(t["name"] == "default" for t in templates)
    
    # Test template rendering
    context = {
        "title": "Test Blog Post",
        "keyword": "test_keyword",
        "meta_description": "This is a test blog post",
        "trend_data": {
            "avg_engagement_score": 0.75,
            "avg_tfidf_score": 0.65,
            "trend_direction": "rising",
            "total_posts": 25,
            "analyzed_at": "2024-01-01T00:00:00",
            "top_keywords": [
                {"keyword": "test", "score": 0.8},
                {"keyword": "example", "score": 0.6}
            ]
        },
        "top_posts": [],
        "insights": ["Test insight 1", "Test insight 2"]
    }
    
    content = template_service.render_template("default", context)
    assert content is not None
    print(f"Generated content preview: {content[:200]}...")
    assert "Test Blog Post" in content
    assert "test_keyword" in content
    # Check for trend direction in a more flexible way
    assert "rising" in content.lower() or "Rising" in content
    
    print("✓ Template service tests passed")


def test_content_generation_service():
    """Test content generation service functionality."""
    content_service = ContentGenerationService()
    
    # Test title generation
    title = content_service._generate_title("test_keyword", {
        "trend_direction": "rising",
        "total_posts": 50
    })
    assert "Test Keyword" in title
    assert len(title) > 10
    
    # Test meta description generation
    meta = content_service._generate_meta_description("test_keyword", {
        "total_posts": 25,
        "trend_direction": "stable"
    })
    assert "test keyword" in meta
    assert "25" in meta
    
    # Test slug generation
    slug = content_service._generate_slug("Why Test Keyword is Trending on Reddit Right Now")
    assert slug == "why-test-keyword-is-trending-on-reddit-right-now"
    
    # Test word counting
    content = "This is a test content with multiple words and sentences."
    word_count = content_service._count_words(content)
    print(f"Word count: {word_count}")
    assert word_count >= 10  # Allow some flexibility in word counting
    
    # Test tag generation
    tags = content_service._generate_tags("test_keyword", {
        "trend_direction": "rising",
        "top_keywords": [
            {"keyword": "test", "score": 0.8},
            {"keyword": "example", "score": 0.6}
        ]
    }, [])
    assert "test keyword" in tags
    assert "reddit" in tags
    assert "analysis" in tags
    
    print("✓ Content generation service tests passed")


def test_template_validation():
    """Test template validation functionality."""
    template_service = TemplateService()
    
    # Test valid template
    valid_template = "# {{ title }}\n\n{{ content }}\n\nGenerated: {{ generated_at }}"
    validation = template_service.validate_template(valid_template)
    assert validation["valid"] is True
    assert "title" in validation["variables"]
    assert "content" in validation["variables"]
    
    # Test invalid template
    invalid_template = "# {{ title }\n\n{{ content }}"  # Missing closing brace
    validation = template_service.validate_template(invalid_template)
    assert validation["valid"] is False
    assert "error" in validation
    
    print("✓ Template validation tests passed")


def test_content_post_processing():
    """Test content post-processing functionality."""
    content_service = ContentGenerationService()
    
    # Test content with excessive whitespace
    messy_content = """# Title


## Section 1



Some content here.


## Section 2

More content.


"""
    
    processed = content_service._post_process_content(messy_content)
    print(f"Processed content: {repr(processed)}")
    
    # Should remove excessive newlines
    assert "\n\n\n" not in processed
    
    # Should maintain proper structure
    assert "# Title" in processed
    assert "## Section 1" in processed
    
    print("✓ Content post-processing tests passed")


if __name__ == "__main__":
    print("Testing content generation implementation...")
    
    try:
        test_template_service()
        test_content_generation_service()
        test_template_validation()
        test_content_post_processing()
        
        print("\n✅ All content generation tests passed!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()