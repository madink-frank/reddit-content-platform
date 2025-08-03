"""
Pydantic schemas for trend analysis.
"""

from datetime import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class TrendMetrics(BaseModel):
    """Schema for trend metrics data."""
    avg_tfidf_score: float = Field(..., description="Average TF-IDF score")
    avg_engagement_score: float = Field(..., description="Average engagement score")
    trend_velocity: float = Field(..., description="Trend velocity (rate of change)")
    total_posts: int = Field(..., description="Total number of posts analyzed")
    analyzed_at: str = Field(..., description="Timestamp when analysis was performed")


class TrendAnalysisRequest(BaseModel):
    """Schema for trend analysis request."""
    keyword_id: int = Field(..., description="ID of the keyword to analyze")
    force_refresh: bool = Field(False, description="Force refresh of cached data")


class TrendAnalysisResponse(BaseModel):
    """Schema for trend analysis response."""
    keyword_id: int = Field(..., description="ID of the analyzed keyword")
    keyword: str = Field(..., description="The keyword that was analyzed")
    trend_data: Dict[str, Any] = Field(..., description="Trend analysis results")
    cached: bool = Field(..., description="Whether the data was retrieved from cache")


class KeywordRanking(BaseModel):
    """Schema for individual keyword ranking."""
    keyword_id: int = Field(..., description="ID of the keyword")
    keyword: str = Field(..., description="The keyword text")
    importance_score: float = Field(..., description="Calculated importance score")
    avg_tfidf_score: float = Field(..., description="Average TF-IDF score")
    avg_engagement_score: float = Field(..., description="Average engagement score")
    trend_velocity: float = Field(..., description="Trend velocity")
    total_posts: int = Field(..., description="Total number of posts for this keyword")


class KeywordRankingResponse(BaseModel):
    """Schema for keyword ranking response."""
    user_id: int = Field(..., description="ID of the user")
    rankings: List[KeywordRanking] = Field(..., description="List of keyword rankings")
    total_keywords: int = Field(..., description="Total number of keywords ranked")


class BulkAnalysisResult(BaseModel):
    """Schema for individual bulk analysis result."""
    keyword_id: int = Field(..., description="ID of the keyword")
    keyword: str = Field(..., description="The keyword text")
    success: bool = Field(..., description="Whether the analysis was successful")
    trend_data: Optional[Dict[str, Any]] = Field(None, description="Trend analysis results")
    error: Optional[str] = Field(None, description="Error message if analysis failed")


class BulkAnalysisResponse(BaseModel):
    """Schema for bulk analysis response."""
    user_id: int = Field(..., description="ID of the user")
    total_keywords: int = Field(..., description="Total number of keywords processed")
    successful_analyses: int = Field(..., description="Number of successful analyses")
    results: List[BulkAnalysisResult] = Field(..., description="Individual analysis results")
    task_id: str = Field(..., description="ID of the Celery task")


class TaskStatusResponse(BaseModel):
    """Schema for task status response."""
    task_id: str = Field(..., description="ID of the task")
    state: str = Field(..., description="Current state of the task")
    current: Optional[int] = Field(None, description="Current progress")
    total: Optional[int] = Field(None, description="Total items to process")
    status: Optional[str] = Field(None, description="Status message")
    result: Optional[Dict[str, Any]] = Field(None, description="Task result if completed")
    error: Optional[str] = Field(None, description="Error message if failed")


class MetricSummary(BaseModel):
    """Schema for metric summary."""
    post_id: int = Field(..., description="ID of the post")
    engagement_score: float = Field(..., description="Engagement score")
    tfidf_score: float = Field(..., description="TF-IDF score")
    trend_velocity: float = Field(..., description="Trend velocity")
    calculated_at: datetime = Field(..., description="When the metric was calculated")


class TrendSummaryResponse(BaseModel):
    """Schema for trend summary response."""
    keyword_id: int = Field(..., description="ID of the keyword")
    keyword: str = Field(..., description="The keyword text")
    metrics: List[MetricSummary] = Field(..., description="List of metrics for posts")
    summary: TrendMetrics = Field(..., description="Summary of trend metrics")


class AnalysisConfiguration(BaseModel):
    """Schema for analysis configuration."""
    max_features: int = Field(1000, description="Maximum number of TF-IDF features")
    ngram_range: tuple = Field((1, 2), description="N-gram range for TF-IDF")
    min_df: int = Field(2, description="Minimum document frequency")
    max_df: float = Field(0.8, description="Maximum document frequency")
    engagement_weight_score: float = Field(0.6, description="Weight for Reddit score in engagement calculation")
    engagement_weight_comments: float = Field(0.4, description="Weight for comments in engagement calculation")


class TrendComparisonRequest(BaseModel):
    """Schema for trend comparison request."""
    keyword_ids: List[int] = Field(..., description="List of keyword IDs to compare")
    time_range_days: int = Field(7, description="Number of days to include in comparison")


class TrendComparisonResponse(BaseModel):
    """Schema for trend comparison response."""
    keywords: List[str] = Field(..., description="List of keywords being compared")
    comparison_data: Dict[str, Any] = Field(..., description="Comparison results")
    time_range_days: int = Field(..., description="Time range used for comparison")
    generated_at: datetime = Field(..., description="When the comparison was generated")


class ScheduledAnalysisConfig(BaseModel):
    """Schema for scheduled analysis configuration."""
    enabled: bool = Field(True, description="Whether scheduled analysis is enabled")
    frequency_hours: int = Field(24, description="Frequency of analysis in hours")
    max_keywords_per_batch: int = Field(50, description="Maximum keywords to process per batch")
    retry_failed: bool = Field(True, description="Whether to retry failed analyses")


class AnalysisHealthCheck(BaseModel):
    """Schema for analysis service health check."""
    service_status: str = Field(..., description="Status of the analysis service")
    redis_connected: bool = Field(..., description="Whether Redis is connected")
    database_connected: bool = Field(..., description="Whether database is connected")
    celery_workers_active: int = Field(..., description="Number of active Celery workers")
    last_analysis_time: Optional[datetime] = Field(None, description="Time of last successful analysis")
    pending_tasks: int = Field(..., description="Number of pending analysis tasks")


class TrendHistoryEntry(BaseModel):
    """Schema for individual trend history entry."""
    timestamp: str = Field(..., description="Timestamp of the trend data point")
    avg_tfidf_score: float = Field(..., description="Average TF-IDF score at this point")
    avg_engagement_score: float = Field(..., description="Average engagement score at this point")
    trend_velocity: float = Field(..., description="Trend velocity at this point")
    total_posts: int = Field(..., description="Total posts at this point")
    confidence_score: float = Field(..., description="Confidence score at this point")


class TrendHistoryResponse(BaseModel):
    """Schema for trend history response."""
    keyword_id: int = Field(..., description="ID of the keyword")
    keyword: str = Field(..., description="The keyword text")
    days_requested: int = Field(..., description="Number of days requested")
    history_count: int = Field(..., description="Number of history entries returned")
    history: List[TrendHistoryEntry] = Field(..., description="Historical trend data")


class EnhancedTrendMetrics(TrendMetrics):
    """Enhanced trend metrics with additional fields."""
    avg_sentiment_score: float = Field(0.0, description="Average sentiment score")
    avg_virality_score: float = Field(0.0, description="Average virality score")
    cache_expires_at: str = Field(..., description="When the cached data expires")
    top_keywords: List[Dict[str, Any]] = Field(default_factory=list, description="Top keywords extracted")
    engagement_distribution: Dict[str, int] = Field(default_factory=dict, description="Distribution of engagement scores")
    trend_direction: str = Field(..., description="Direction of the trend (rising/falling/stable)")
    confidence_score: float = Field(..., description="Confidence score for the analysis")


class TrendSummaryKeyword(BaseModel):
    """Schema for keyword in trend summary."""
    keyword_id: int = Field(..., description="ID of the keyword")
    keyword: str = Field(..., description="The keyword text")
    trend_data: Dict[str, Any] = Field(..., description="Trend data for the keyword")


class TrendSummaryData(BaseModel):
    """Schema for trend summary data."""
    total_keywords: int = Field(..., description="Total number of keywords")
    total_posts: int = Field(..., description="Total number of posts across all keywords")
    avg_engagement_score: float = Field(..., description="Average engagement score across all keywords")
    avg_tfidf_score: float = Field(..., description="Average TF-IDF score across all keywords")
    generated_at: str = Field(..., description="When the summary was generated")


class TrendSummaryResponse(BaseModel):
    """Schema for comprehensive trend summary response."""
    user_id: int = Field(..., description="ID of the user")
    keywords: List[TrendSummaryKeyword] = Field(..., description="Keyword trend data")
    summary: TrendSummaryData = Field(..., description="Overall summary statistics")


class CacheStatistics(BaseModel):
    """Schema for cache statistics."""
    cache_info: Dict[str, Any] = Field(..., description="General cache information")
    trend_cache_keys: int = Field(..., description="Number of trend cache keys")
    ranking_cache_keys: int = Field(..., description="Number of ranking cache keys")
    history_cache_keys: int = Field(..., description="Number of history cache keys")
    summary_cache_keys: int = Field(..., description="Number of summary cache keys")
    total_trend_related_keys: int = Field(..., description="Total trend-related cache keys")