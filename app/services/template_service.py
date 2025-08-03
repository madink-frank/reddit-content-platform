"""
Template service for managing blog post templates.
"""

import os
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from jinja2 import Environment, FileSystemLoader, Template, TemplateError
from pathlib import Path

logger = logging.getLogger(__name__)


class TemplateService:
    """
    Service for managing and rendering blog post templates.
    """
    
    def __init__(self):
        self.templates_dir = Path("app/templates/blog")
        self.templates_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize Jinja2 environment
        self.jinja_env = Environment(
            loader=FileSystemLoader(str(self.templates_dir)),
            autoescape=True,
            trim_blocks=True,
            lstrip_blocks=True
        )
        
        # Initialize default templates if they don't exist
        self._initialize_default_templates()
    
    def _initialize_default_templates(self):
        """Initialize default blog post templates."""
        default_templates = {
            "default": {
                "name": "Default Blog Post",
                "description": "Standard blog post template with trend analysis",
                "template": """# {{ title }}

{{ meta_description }}

## Overview

Based on our analysis of Reddit discussions around "{{ keyword }}", we've identified some interesting trends and insights.

{% if trend_data %}
## Trend Analysis

- **Average Engagement Score**: {{ "%.2f"|format(trend_data.avg_engagement_score) }}
- **TF-IDF Score**: {{ "%.2f"|format(trend_data.avg_tfidf_score) }}
- **Trend Direction**: {{ trend_data.trend_direction|title }}
- **Total Posts Analyzed**: {{ trend_data.total_posts }}
- **Analysis Date**: {{ trend_data.analyzed_at[:10] }}

{% if trend_data.top_keywords %}
### Key Topics
{% for kw in trend_data.top_keywords[:5] %}
- **{{ kw.keyword }}** (Score: {{ "%.3f"|format(kw.score) }})
{% endfor %}
{% endif %}
{% endif %}

{% if top_posts %}
## Top Discussions

Here are the most engaging posts we found:

{% for post in top_posts %}
### {{ post.title }}

**Score**: {{ post.score }} | **Comments**: {{ post.num_comments }} | **Author**: u/{{ post.author }}

{{ post.content[:300] }}{% if post.content|length > 300 %}...{% endif %}

[View on Reddit]({{ post.url }})

---
{% endfor %}
{% endif %}

## Insights

{% if insights %}
{% for insight in insights %}
- {{ insight }}
{% endfor %}
{% else %}
- The community shows {{ trend_data.trend_direction }} interest in {{ keyword }}
- Engagement levels are {{ "high" if trend_data.avg_engagement_score > 0.7 else "moderate" if trend_data.avg_engagement_score > 0.3 else "low" }}
- This topic has generated {{ trend_data.total_posts }} discussions recently
{% endif %}

## Conclusion

{{ conclusion or "The analysis of Reddit discussions around '" + keyword + "' reveals valuable insights into community sentiment and trending topics. This data can help inform content strategy and community engagement efforts." }}

---

*This analysis was generated on {{ generated_at }} based on Reddit data collected through our automated crawling system.*
"""
            },
            "news": {
                "name": "News Style",
                "description": "News-style blog post template",
                "template": """# {{ title }}

*{{ generated_at[:10] }} - Reddit Analysis Report*

{{ meta_description }}

{% if trend_data %}
**{{ keyword|title }}** is {{ trend_data.trend_direction }} in popularity on Reddit, with {{ trend_data.total_posts }} posts analyzed and an average engagement score of {{ "%.1f"|format(trend_data.avg_engagement_score * 100) }}%.
{% endif %}

## What's Happening

{% if top_posts %}
{% for post in top_posts[:3] %}
**{{ post.title }}** ({{ post.score }} upvotes, {{ post.num_comments }} comments)
{{ post.content[:200] }}{% if post.content|length > 200 %}...{% endif %}

{% endfor %}
{% endif %}

{% if trend_data and trend_data.top_keywords %}
## Trending Topics

The most discussed aspects include:
{% for kw in trend_data.top_keywords[:5] %}
- {{ kw.keyword|title }}
{% endfor %}
{% endif %}

## Community Sentiment

{% if trend_data %}
Based on our analysis, the Reddit community's interest in {{ keyword }} is {{ trend_data.trend_direction }}. 
{% if trend_data.avg_engagement_score > 0.7 %}
The high engagement scores suggest strong community interest and active participation in discussions.
{% elif trend_data.avg_engagement_score > 0.3 %}
Moderate engagement levels indicate steady but not overwhelming interest from the community.
{% else %}
Lower engagement scores suggest this topic may be niche or emerging within the Reddit community.
{% endif %}
{% endif %}

## Key Takeaways

{% if insights %}
{% for insight in insights %}
- {{ insight }}
{% endfor %}
{% else %}
- {{ keyword|title }} discussions are {{ trend_data.trend_direction }} on Reddit
- Community engagement is {{ "strong" if trend_data.avg_engagement_score > 0.7 else "moderate" if trend_data.avg_engagement_score > 0.3 else "emerging" }}
- {{ trend_data.total_posts }} posts were analyzed for this report
{% endif %}

---

*Data sourced from Reddit discussions. Analysis generated {{ generated_at }}.*
"""
            },
            "listicle": {
                "name": "Listicle Style",
                "description": "List-based blog post template",
                "template": """# {{ title }}

{{ meta_description }}

{% if trend_data %}
*Based on analysis of {{ trend_data.total_posts }} Reddit posts about {{ keyword }}*
{% endif %}

{% if top_posts %}
{% for post in top_posts %}
## {{ loop.index }}. {{ post.title }}

**{{ post.score }} upvotes | {{ post.num_comments }} comments | u/{{ post.author }}**

{{ post.content[:250] }}{% if post.content|length > 250 %}...{% endif %}

**Why it matters**: {% if post.score > 1000 %}This highly upvoted post shows strong community agreement.{% elif post.num_comments > 50 %}The high comment count indicates active discussion and debate.{% else %}This post represents a common perspective in the community.{% endif %}

[Read full discussion →]({{ post.url }})

---
{% endfor %}
{% endif %}

## Bonus: Trend Insights

{% if trend_data and trend_data.top_keywords %}
**Most discussed topics**:
{% for kw in trend_data.top_keywords[:5] %}
- {{ kw.keyword|title }} ({{ "%.1f"|format(kw.score * 100) }}% relevance)
{% endfor %}
{% endif %}

{% if trend_data %}
**Community engagement**: {{ "High" if trend_data.avg_engagement_score > 0.7 else "Moderate" if trend_data.avg_engagement_score > 0.3 else "Growing" }} ({{ "%.1f"|format(trend_data.avg_engagement_score * 100) }}%)

**Trend direction**: {{ trend_data.trend_direction|title }}
{% endif %}

## What This Means

{{ conclusion or "These Reddit discussions show the diverse perspectives and active engagement around " + keyword + ". The community's " + trend_data.trend_direction + " interest suggests this topic will continue to generate discussion." }}

---

*Analysis based on Reddit data collected {{ generated_at[:10] }}. Engagement scores and trends calculated using TF-IDF analysis.*
"""
            }
        }
        
        # Create template files
        for template_name, template_data in default_templates.items():
            template_file = self.templates_dir / f"{template_name}.md"
            if not template_file.exists():
                template_file.write_text(template_data["template"])
                
                # Also create metadata file
                metadata_file = self.templates_dir / f"{template_name}.json"
                metadata = {
                    "name": template_data["name"],
                    "description": template_data["description"],
                    "variables": self._extract_template_variables(template_data["template"])
                }
                metadata_file.write_text(json.dumps(metadata, indent=2))
    
    def _extract_template_variables(self, template_content: str) -> List[str]:
        """Extract variables from template content."""
        import re
        # Find Jinja2 variables like {{ variable }}
        variables = re.findall(r'\{\{\s*([^}]+)\s*\}\}', template_content)
        # Clean up variables (remove filters and functions)
        cleaned_vars = []
        for var in variables:
            # Remove filters and function calls
            clean_var = var.split('|')[0].split('(')[0].strip()
            if clean_var not in cleaned_vars and not clean_var.startswith('"'):
                cleaned_vars.append(clean_var)
        return cleaned_vars
    
    def get_available_templates(self) -> List[Dict[str, Any]]:
        """Get list of available templates."""
        templates = []
        
        for template_file in self.templates_dir.glob("*.md"):
            template_name = template_file.stem
            metadata_file = self.templates_dir / f"{template_name}.json"
            
            if metadata_file.exists():
                try:
                    metadata = json.loads(metadata_file.read_text())
                    templates.append({
                        "name": template_name,
                        "display_name": metadata.get("name", template_name),
                        "description": metadata.get("description", ""),
                        "variables": metadata.get("variables", [])
                    })
                except json.JSONDecodeError:
                    logger.warning(f"Invalid metadata file: {metadata_file}")
        
        return templates
    
    def get_template(self, template_name: str) -> Optional[Template]:
        """Get a template by name."""
        try:
            return self.jinja_env.get_template(f"{template_name}.md")
        except TemplateError as e:
            logger.error(f"Error loading template {template_name}: {str(e)}")
            return None
    
    def render_template(
        self, 
        template_name: str, 
        context: Dict[str, Any]
    ) -> Optional[str]:
        """
        Render a template with the given context.
        
        Args:
            template_name: Name of the template to render
            context: Template context variables
            
        Returns:
            Rendered template content or None if error
        """
        try:
            template = self.get_template(template_name)
            if not template:
                return None
            
            # Add default context variables
            default_context = {
                "generated_at": datetime.utcnow().isoformat(),
            }
            
            # Merge contexts
            render_context = {**default_context, **context}
            
            return template.render(**render_context)
            
        except TemplateError as e:
            logger.error(f"Error rendering template {template_name}: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error rendering template {template_name}: {str(e)}")
            return None
    
    def validate_template(self, template_content: str) -> Dict[str, Any]:
        """
        Validate template syntax and return information.
        
        Args:
            template_content: Template content to validate
            
        Returns:
            Validation result with status and details
        """
        try:
            # Try to parse the template
            template = self.jinja_env.from_string(template_content)
            
            # Extract variables
            variables = self._extract_template_variables(template_content)
            
            return {
                "valid": True,
                "variables": variables,
                "message": "Template is valid"
            }
            
        except TemplateError as e:
            return {
                "valid": False,
                "error": str(e),
                "message": "Template syntax error"
            }
        except Exception as e:
            return {
                "valid": False,
                "error": str(e),
                "message": "Unexpected validation error"
            }
    
    def create_custom_template(
        self, 
        name: str, 
        content: str, 
        description: str = ""
    ) -> bool:
        """
        Create a custom template.
        
        Args:
            name: Template name
            content: Template content
            description: Template description
            
        Returns:
            True if template was created successfully
        """
        try:
            # Validate template first
            validation = self.validate_template(content)
            if not validation["valid"]:
                logger.error(f"Invalid template content: {validation['error']}")
                return False
            
            # Save template file
            template_file = self.templates_dir / f"{name}.md"
            template_file.write_text(content)
            
            # Save metadata
            metadata = {
                "name": name.replace("_", " ").title(),
                "description": description,
                "variables": validation["variables"],
                "created_at": datetime.utcnow().isoformat(),
                "custom": True
            }
            
            metadata_file = self.templates_dir / f"{name}.json"
            metadata_file.write_text(json.dumps(metadata, indent=2))
            
            logger.info(f"Created custom template: {name}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating custom template {name}: {str(e)}")
            return False
    
    def delete_template(self, name: str) -> bool:
        """
        Delete a custom template.
        
        Args:
            name: Template name to delete
            
        Returns:
            True if template was deleted successfully
        """
        try:
            # Check if it's a custom template
            metadata_file = self.templates_dir / f"{name}.json"
            if metadata_file.exists():
                metadata = json.loads(metadata_file.read_text())
                if not metadata.get("custom", False):
                    logger.error(f"Cannot delete built-in template: {name}")
                    return False
            
            # Delete template and metadata files
            template_file = self.templates_dir / f"{name}.md"
            if template_file.exists():
                template_file.unlink()
            
            if metadata_file.exists():
                metadata_file.unlink()
            
            logger.info(f"Deleted custom template: {name}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting template {name}: {str(e)}")
            return False