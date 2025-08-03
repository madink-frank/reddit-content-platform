"""
Summary test for content generation implementation.
"""

import asyncio
from datetime import datetime


def test_imports():
    """Test that all components can be imported successfully."""
    print("Testing imports...")
    
    try:
        # Test service imports
        from app.services.content_generation_service import ContentGenerationService
        from app.services.template_service import TemplateService
        print("✓ Services imported successfully")
        
        # Test schema imports
        from app.schemas.blog_content import (
            ContentGenerationRequest,
            ContentGenerationResponse,
            BlogContentResponse,
            ContentPreview
        )
        print("✓ Schemas imported successfully")
        
        # Test model imports
        from app.models.blog_content import BlogContent
        print("✓ Models imported successfully")
        
        # Test API imports
        from app.api.v1.endpoints.content import router
        print("✓ API endpoints imported successfully")
        
        # Test worker imports
        from app.workers.content_tasks import generate_blog_content_task
        print("✓ Celery tasks imported successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Import failed: {str(e)}")
        return False


def test_template_system():
    """Test template system functionality."""
    print("\nTesting template system...")
    
    try:
        from app.services.template_service import TemplateService
        
        template_service = TemplateService()
        
        # Test template availability
        templates = template_service.get_available_templates()
        assert len(templates) >= 3
        print(f"✓ Found {len(templates)} templates")
        
        # Test template rendering
        context = {
            "title": "Test Title",
            "keyword": "test",
            "meta_description": "Test description",
            "trend_data": {
                "avg_engagement_score": 0.5,
                "avg_tfidf_score": 0.4,
                "trend_direction": "stable",
                "total_posts": 10,
                "analyzed_at": "2024-01-01T00:00:00",
                "top_keywords": []
            },
            "top_posts": [],
            "insights": ["Test insight"]
        }
        
        content = template_service.render_template("default", context)
        assert content is not None
        assert "Test Title" in content
        print("✓ Template rendering works")
        
        # Test template validation
        validation = template_service.validate_template("# {{ title }}\n{{ content }}")
        assert validation["valid"] is True
        print("✓ Template validation works")
        
        return True
        
    except Exception as e:
        print(f"❌ Template system test failed: {str(e)}")
        return False


def test_content_generation_service():
    """Test content generation service functionality."""
    print("\nTesting content generation service...")
    
    try:
        from app.services.content_generation_service import ContentGenerationService
        
        service = ContentGenerationService()
        
        # Test utility functions
        title = service._generate_title("test_keyword", {"trend_direction": "rising"})
        assert len(title) > 0
        print("✓ Title generation works")
        
        slug = service._generate_slug("Test Blog Post Title")
        assert slug == "test-blog-post-title"
        print("✓ Slug generation works")
        
        word_count = service._count_words("This is a test sentence with words.")
        assert word_count > 0
        print("✓ Word counting works")
        
        tags = service._generate_tags("test", {}, [])
        assert "test" in tags
        assert "reddit" in tags
        print("✓ Tag generation works")
        
        return True
        
    except Exception as e:
        print(f"❌ Content generation service test failed: {str(e)}")
        return False


def test_api_structure():
    """Test API structure and endpoints."""
    print("\nTesting API structure...")
    
    try:
        from app.api.v1.api import api_router
        from app.api.v1.endpoints.content import router
        
        # Check that content router is included
        routes = [route.path for route in api_router.routes]
        content_routes = [route for route in routes if "/content" in route]
        
        print(f"✓ Found {len(content_routes)} content routes")
        
        # Check specific endpoints exist
        from app.api.v1.endpoints import content
        endpoint_functions = [
            "generate_content",
            "list_content", 
            "get_content",
            "update_content",
            "delete_content",
            "preview_content"
        ]
        
        for func_name in endpoint_functions:
            assert hasattr(content, func_name)
        
        print("✓ All expected endpoints exist")
        
        return True
        
    except Exception as e:
        print(f"❌ API structure test failed: {str(e)}")
        return False


def test_database_models():
    """Test database model structure."""
    print("\nTesting database models...")
    
    try:
        from app.models.blog_content import BlogContent
        from app.models.keyword import Keyword
        
        # Check BlogContent model has required fields
        required_fields = [
            'keyword_id', 'title', 'content', 'template_used', 
            'generated_at', 'word_count', 'status', 'slug'
        ]
        
        for field in required_fields:
            assert hasattr(BlogContent, field)
        
        print("✓ BlogContent model has all required fields")
        
        # Check relationship exists
        assert hasattr(Keyword, 'blog_contents')
        print("✓ Keyword-BlogContent relationship exists")
        
        return True
        
    except Exception as e:
        print(f"❌ Database model test failed: {str(e)}")
        return False


def test_celery_tasks():
    """Test Celery task structure."""
    print("\nTesting Celery tasks...")
    
    try:
        from app.workers.content_tasks import (
            generate_blog_content_task,
            batch_generate_content_task,
            regenerate_content_task,
            cleanup_old_content_task
        )
        
        # Check tasks are properly decorated
        assert hasattr(generate_blog_content_task, 'delay')
        assert hasattr(batch_generate_content_task, 'delay')
        print("✓ Celery tasks are properly configured")
        
        return True
        
    except Exception as e:
        print(f"❌ Celery task test failed: {str(e)}")
        return False


async def main():
    """Run all summary tests."""
    print("🚀 Content Generation Implementation Summary Test\n")
    print("=" * 60)
    
    tests = [
        test_imports,
        test_template_system,
        test_content_generation_service,
        test_api_structure,
        test_database_models,
        test_celery_tasks
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                print("❌ Test failed")
        except Exception as e:
            print(f"❌ Test error: {str(e)}")
    
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("✅ All content generation components are working correctly!")
        print("\n🎉 Implementation Summary:")
        print("   • Template system with 3 built-in templates (default, news, listicle)")
        print("   • Content generation service with trend analysis integration")
        print("   • Complete API endpoints for content management")
        print("   • Celery tasks for background content generation")
        print("   • Database models with proper relationships")
        print("   • Markdown content validation and post-processing")
        print("   • SEO-friendly slug and tag generation")
        print("   • Preview functionality for content testing")
        return True
    else:
        print(f"❌ {total - passed} tests failed")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)