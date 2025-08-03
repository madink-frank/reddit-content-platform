# {{ title }}

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
