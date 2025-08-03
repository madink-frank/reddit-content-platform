# {{ title }}

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
