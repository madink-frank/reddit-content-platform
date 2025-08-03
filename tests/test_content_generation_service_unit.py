"""
Unit tests for Content Generation Service.
"""
import pytest
from unittest.mock import MagicMock, AsyncMock, patch, mock_open
from datetime import datetime
import json

from app.services.content_generation_service import ContentGenerationService
from app.services.template_service import TemplateService
from app.models.blog_content import BlogContent
from app.schemas.blog_content import BlogContentCreate
from app.schemas.trend import TrendMetrics


class TestContentGenerationService:
    """Test cases for ContentGenerationService."""
    
    @pytest.fixture
    def content_service(self):
        """Create ContentGenerationService instance for testing."""
        return ContentGenerationService()
    
    @pytest.fixture
    def template_service(self):
        """Create TemplateService instance for testing."""
        return TemplateService()
    
    @pytest.fixture
    def sample_trend_metrics(self, sample_keyword):
        """Sample trend metrics for testing."""
        return TrendMetrics(
            keyword_id=sample_keyword.id,
            tfidf_scores={
                "python": 0.85,
                "machine": 0.72,
                "learning": 0.68,
                "data": 0.65,
                "science": 0.60
            },
            average_engagement=175.5,
            trend_velocity=0.25,
            total_posts=15,
            analysis_date=datetime.utcnow()
        )
    
    @pytest.fixture
    def sample_template_content(self):
        """Sample template content for testing."""
        return {
            "title_template": "# {keyword} Trends: {trend_summary}",
            "intro_template": "Recent analysis of {keyword} discussions shows {trend_direction} activity.",
            "sections": [
                {
                    "title": "Key Insights",
                    "template": "The most discussed topics include: {top_keywords}"
                },
                {
                    "title": "Engagement Analysis", 
                    "template": "Average engagement score: {engagement_score}"
                }
            ],
            "conclusion_template": "Based on current trends, {keyword} shows {trend_prediction}."
        }
    
    @pytest.mark.asyncio
    async def test_generate_blog_content_success(self, content_service, sample_keyword, sample_trend_metrics):
        """Test successful blog content generation."""
        # Mock template service
        with patch.object(content_service, 'template_service') as mock_template:
            mock_template.get_template.return_value = {
                "title_template": "# {keyword} Trends Analysis",
                "content_template": "Analysis of {keyword} shows {total_posts} posts with average engagement of {average_engagement}."
            }
            
            # Mock database operations
            content_service.db.add = MagicMock()
            content_service.db.commit = MagicMock()
            content_service.db.refresh = MagicMock()
            
            result = await content_service.generate_blog_content(
                keyword_id=sample_keyword.id,
                trend_metrics=sample_trend_metrics,
                template_type="default"
            )
            
            assert isinstance(result, BlogContent)
            assert result.keyword_id == sample_keyword.id
            assert result.template_used == "default"
            assert len(result.content) > 0
            assert result.title is not None
    
    @pytest.mark.asyncio
    async def test_generate_blog_content_invalid_keyword(self, content_service, sample_trend_metrics):
        """Test blog content generation with invalid keyword ID."""
        with pytest.raises(ValueError, match="Invalid keyword ID"):
            await content_service.generate_blog_content(
                keyword_id=0,
                trend_metrics=sample_trend_metrics,
                template_type="default"
            )
    
    @pytest.mark.asyncio
    async def test_generate_blog_content_no_trend_data(self, content_service, sample_keyword):
        """Test blog content generation without trend data."""
        empty_metrics = TrendMetrics(
            keyword_id=sample_keyword.id,
            tfidf_scores={},
            average_engagement=0.0,
            trend_velocity=0.0,
            total_posts=0,
            analysis_date=datetime.utcnow()
        )
        
        with pytest.raises(ValueError, match="Insufficient trend data"):
            await content_service.generate_blog_content(
                keyword_id=sample_keyword.id,
                trend_metrics=empty_metrics,
                template_type="default"
            )
    
    @pytest.mark.asyncio
    async def test_apply_template_success(self, content_service, sample_trend_metrics, sample_template_content):
        """Test successful template application."""
        template_data = {
            "keyword": "python",
            "trend_summary": "increasing popularity",
            "trend_direction": "upward",
            "top_keywords": "machine learning, data science",
            "engagement_score": "175.5",
            "trend_prediction": "continued growth"
        }
        
        result = content_service.apply_template(sample_template_content, template_data)
        
        assert isinstance(result, str)
        assert "python" in result
        assert "increasing popularity" in result
        assert "175.5" in result
        assert len(result) > 0
    
    @pytest.mark.asyncio
    async def test_apply_template_missing_variables(self, content_service, sample_template_content):
        """Test template application with missing variables."""
        incomplete_data = {
            "keyword": "python"
            # Missing other required variables
        }
        
        # Should handle missing variables gracefully
        result = content_service.apply_template(sample_template_content, incomplete_data)
        
        assert isinstance(result, str)
        assert "python" in result
    
    @pytest.mark.asyncio
    async def test_extract_template_variables(self, content_service, sample_trend_metrics, sample_keyword):
        """Test extraction of template variables from trend data."""
        variables = content_service.extract_template_variables(
            keyword="python",
            trend_metrics=sample_trend_metrics
        )
        
        assert isinstance(variables, dict)
        assert variables["keyword"] == "python"
        assert variables["total_posts"] == str(sample_trend_metrics.total_posts)
        assert variables["average_engagement"] == str(sample_trend_metrics.average_engagement)
        assert "top_keywords" in variables
        assert "trend_direction" in variables
    
    @pytest.mark.asyncio
    async def test_determine_trend_direction_upward(self, content_service):
        """Test trend direction determination for upward trend."""
        direction = content_service.determine_trend_direction(
            trend_velocity=0.25,
            average_engagement=175.5
        )
        
        assert direction == "upward"
    
    @pytest.mark.asyncio
    async def test_determine_trend_direction_downward(self, content_service):
        """Test trend direction determination for downward trend."""
        direction = content_service.determine_trend_direction(
            trend_velocity=-0.15,
            average_engagement=50.0
        )
        
        assert direction == "downward"
    
    @pytest.mark.asyncio
    async def test_determine_trend_direction_stable(self, content_service):
        """Test trend direction determination for stable trend."""
        direction = content_service.determine_trend_direction(
            trend_velocity=0.02,
            average_engagement=100.0
        )
        
        assert direction == "stable"
    
    @pytest.mark.asyncio
    async def test_format_top_keywords(self, content_service):
        """Test formatting of top keywords."""
        tfidf_scores = {
            "python": 0.85,
            "machine": 0.72,
            "learning": 0.68,
            "data": 0.65,
            "science": 0.60
        }
        
        formatted = content_service.format_top_keywords(tfidf_scores, limit=3)
        
        assert isinstance(formatted, str)
        assert "python" in formatted
        assert "machine" in formatted
        assert "learning" in formatted
        # Should not include lower-scored keywords
        assert "science" not in formatted
    
    @pytest.mark.asyncio
    async def test_generate_content_title(self, content_service, sample_trend_metrics):
        """Test content title generation."""
        title = content_service.generate_content_title(
            keyword="python",
            trend_metrics=sample_trend_metrics,
            template_type="default"
        )
        
        assert isinstance(title, str)
        assert len(title) > 0
        assert "python" in title.lower()
    
    @pytest.mark.asyncio
    async def test_generate_content_summary(self, content_service, sample_trend_metrics):
        """Test content summary generation."""
        summary = content_service.generate_content_summary(
            keyword="python",
            trend_metrics=sample_trend_metrics
        )
        
        assert isinstance(summary, str)
        assert len(summary) > 0
        assert len(summary) <= 200  # Summary should be concise
        assert "python" in summary.lower()
    
    @pytest.mark.asyncio
    async def test_validate_generated_content_valid(self, content_service):
        """Test validation of valid generated content."""
        valid_content = """
        # Python Trends Analysis
        
        ## Introduction
        Recent analysis shows interesting trends.
        
        ## Key Insights
        - Python remains popular
        - Machine learning is trending
        
        ## Conclusion
        The trend continues upward.
        """
        
        is_valid = content_service.validate_generated_content(valid_content)
        
        assert is_valid is True
    
    @pytest.mark.asyncio
    async def test_validate_generated_content_invalid(self, content_service):
        """Test validation of invalid generated content."""
        invalid_content = "Short content"  # Too short
        
        is_valid = content_service.validate_generated_content(invalid_content)
        
        assert is_valid is False
    
    @pytest.mark.asyncio
    async def test_save_generated_content_success(self, content_service, sample_keyword):
        """Test successful saving of generated content."""
        content_data = BlogContentCreate(
            keyword_id=sample_keyword.id,
            title="Test Blog Post",
            content="# Test Content\n\nThis is test content.",
            template_used="default",
            status="draft"
        )
        
        # Mock database operations
        content_service.db.add = MagicMock()
        content_service.db.commit = MagicMock()
        content_service.db.refresh = MagicMock()
        
        result = await content_service.save_generated_content(content_data)
        
        assert isinstance(result, BlogContent)
        content_service.db.add.assert_called_once()
        content_service.db.commit.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_content_by_id_success(self, content_service, sample_blog_content):
        """Test retrieving content by ID."""
        # Mock database query
        content_service.db.query.return_value.filter.return_value.first.return_value = sample_blog_content
        
        result = await content_service.get_content_by_id(sample_blog_content.id)
        
        assert result == sample_blog_content
    
    @pytest.mark.asyncio
    async def test_get_content_by_id_not_found(self, content_service):
        """Test retrieving non-existent content."""
        # Mock database query returning None
        content_service.db.query.return_value.filter.return_value.first.return_value = None
        
        result = await content_service.get_content_by_id(999)
        
        assert result is None
    
    @pytest.mark.asyncio
    async def test_update_content_status(self, content_service, sample_blog_content):
        """Test updating content status."""
        # Mock database operations
        content_service.db.query.return_value.filter.return_value.first.return_value = sample_blog_content
        content_service.db.commit = MagicMock()
        content_service.db.refresh = MagicMock()
        
        result = await content_service.update_content_status(
            content_id=sample_blog_content.id,
            status="published"
        )
        
        assert result.status == "published"
        content_service.db.commit.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_delete_content_success(self, content_service, sample_blog_content):
        """Test successful content deletion."""
        # Mock database operations
        content_service.db.query.return_value.filter.return_value.first.return_value = sample_blog_content
        content_service.db.delete = MagicMock()
        content_service.db.commit = MagicMock()
        
        result = await content_service.delete_content(sample_blog_content.id)
        
        assert result is True
        content_service.db.delete.assert_called_once_with(sample_blog_content)
        content_service.db.commit.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_content_by_keyword_success(self, content_service, sample_keyword, sample_blog_content):
        """Test retrieving content by keyword."""
        # Mock database query
        content_service.db.query.return_value.filter.return_value.all.return_value = [sample_blog_content]
        
        result = await content_service.get_content_by_keyword(sample_keyword.id)
        
        assert len(result) == 1
        assert result[0] == sample_blog_content
    
    @pytest.mark.asyncio
    async def test_generate_content_metadata(self, content_service, sample_trend_metrics):
        """Test generation of content metadata."""
        metadata = content_service.generate_content_metadata(
            keyword="python",
            trend_metrics=sample_trend_metrics
        )
        
        assert isinstance(metadata, dict)
        assert "tags" in metadata
        assert "category" in metadata
        assert "estimated_read_time" in metadata
        assert "seo_keywords" in metadata
    
    @pytest.mark.asyncio
    async def test_estimate_reading_time(self, content_service):
        """Test reading time estimation."""
        content = "This is a test content. " * 100  # ~100 words
        
        reading_time = content_service.estimate_reading_time(content)
        
        assert isinstance(reading_time, int)
        assert reading_time > 0
    
    @pytest.mark.asyncio
    async def test_extract_seo_keywords(self, content_service):
        """Test SEO keyword extraction."""
        content = """
        # Python Machine Learning Tutorial
        
        Learn Python for machine learning and data science.
        This tutorial covers scikit-learn, pandas, and numpy.
        """
        
        seo_keywords = content_service.extract_seo_keywords(content, max_keywords=5)
        
        assert isinstance(seo_keywords, list)
        assert len(seo_keywords) <= 5
        assert all(isinstance(kw, str) for kw in seo_keywords)
    
    @pytest.mark.asyncio
    async def test_generate_content_outline(self, content_service, sample_trend_metrics):
        """Test content outline generation."""
        outline = content_service.generate_content_outline(
            keyword="python",
            trend_metrics=sample_trend_metrics,
            template_type="default"
        )
        
        assert isinstance(outline, list)
        assert len(outline) > 0
        
        for section in outline:
            assert "title" in section
            assert "content_points" in section
    
    @pytest.mark.asyncio
    async def test_enhance_content_with_data(self, content_service, sample_trend_metrics):
        """Test content enhancement with trend data."""
        base_content = "# Python Trends\n\nPython is popular."
        
        enhanced_content = content_service.enhance_content_with_data(
            content=base_content,
            trend_metrics=sample_trend_metrics
        )
        
        assert isinstance(enhanced_content, str)
        assert len(enhanced_content) > len(base_content)
        assert str(sample_trend_metrics.total_posts) in enhanced_content
        assert str(sample_trend_metrics.average_engagement) in enhanced_content


class TestTemplateService:
    """Test cases for TemplateService."""
    
    @pytest.fixture
    def template_service(self):
        """Create TemplateService instance for testing."""
        return TemplateService()
    
    @pytest.mark.asyncio
    async def test_get_template_success(self, template_service):
        """Test successful template retrieval."""
        template_content = {
            "title_template": "# {keyword} Analysis",
            "content_template": "Analysis of {keyword} trends."
        }
        
        with patch("builtins.open", mock_open(read_data=json.dumps(template_content))):
            template = template_service.get_template("default")
            
            assert template == template_content
    
    @pytest.mark.asyncio
    async def test_get_template_not_found(self, template_service):
        """Test template retrieval when file doesn't exist."""
        with patch("builtins.open", side_effect=FileNotFoundError):
            with pytest.raises(ValueError, match="Template not found"):
                template_service.get_template("nonexistent")
    
    @pytest.mark.asyncio
    async def test_list_available_templates(self, template_service):
        """Test listing available templates."""
        with patch("os.listdir", return_value=["default.json", "news.json", "listicle.json"]):
            templates = template_service.list_available_templates()
            
            assert "default" in templates
            assert "news" in templates
            assert "listicle" in templates
    
    @pytest.mark.asyncio
    async def test_validate_template_valid(self, template_service):
        """Test validation of valid template."""
        valid_template = {
            "title_template": "# {keyword} Analysis",
            "content_template": "Content about {keyword}",
            "sections": [
                {"title": "Introduction", "template": "Intro text"}
            ]
        }
        
        is_valid = template_service.validate_template(valid_template)
        
        assert is_valid is True
    
    @pytest.mark.asyncio
    async def test_validate_template_invalid(self, template_service):
        """Test validation of invalid template."""
        invalid_template = {
            "title_template": "# Static Title"  # Missing required fields
        }
        
        is_valid = template_service.validate_template(invalid_template)
        
        assert is_valid is False