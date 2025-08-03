# {{ title }}

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
