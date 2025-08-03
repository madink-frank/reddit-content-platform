"""
Celery tasks for trend analysis and metrics calculation.
"""

import logging
from typing import Dict, Any
from celery import current_task
from sqlalchemy.orm import Session

from app.core.celery_app import celery_app
from app.core.database import get_db
from app.services.trend_analysis_service import trend_analysis_service
from app.models.keyword import Keyword
from app.models.process_log import ProcessLog

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, name="analyze_keyword_trends")
def analyze_keyword_trends_task(self, keyword_id: int, user_id: int) -> Dict[str, Any]:
    """
    Celery task to analyze trends for a specific keyword.
    
    Args:
        keyword_id: ID of the keyword to analyze
        user_id: ID of the user who owns the keyword
        
    Returns:
        Dictionary containing analysis results
    """
    task_id = self.request.id
    db = next(get_db())
    
    try:
        # Log task start
        process_log = ProcessLog(
            user_id=user_id,
            task_type="trend_analysis",
            status="running",
            task_id=task_id
        )
        db.add(process_log)
        db.commit()
        
        logger.info(f"Starting trend analysis for keyword_id: {keyword_id}")
        
        # Update task progress
        current_task.update_state(
            state='PROGRESS',
            meta={'current': 10, 'total': 100, 'status': 'Initializing analysis...'}
        )
        
        # Verify keyword exists and belongs to user
        keyword = db.query(Keyword).filter(
            Keyword.id == keyword_id,
            Keyword.user_id == user_id
        ).first()
        
        if not keyword:
            raise ValueError(f"Keyword {keyword_id} not found or doesn't belong to user {user_id}")
        
        current_task.update_state(
            state='PROGRESS',
            meta={'current': 30, 'total': 100, 'status': 'Calculating TF-IDF scores...'}
        )
        
        # Perform trend analysis
        trend_data = trend_analysis_service.analyze_keyword_trends(keyword_id, db)
        
        current_task.update_state(
            state='PROGRESS',
            meta={'current': 80, 'total': 100, 'status': 'Storing results...'}
        )
        
        # Update process log with success
        process_log.status = "completed"
        process_log.completed_at = db.func.now()
        db.commit()
        
        current_task.update_state(
            state='SUCCESS',
            meta={'current': 100, 'total': 100, 'status': 'Analysis completed successfully'}
        )
        
        logger.info(f"Trend analysis completed for keyword_id: {keyword_id}")
        
        return {
            "success": True,
            "keyword_id": keyword_id,
            "keyword": keyword.keyword,
            "trend_data": trend_data,
            "task_id": task_id
        }
        
    except Exception as e:
        error_msg = f"Error analyzing trends for keyword_id {keyword_id}: {str(e)}"
        logger.error(error_msg)
        
        # Update process log with error
        try:
            process_log.status = "failed"
            process_log.error_message = error_msg
            process_log.completed_at = db.func.now()
            db.commit()
        except:
            pass
        
        current_task.update_state(
            state='FAILURE',
            meta={'error': error_msg}
        )
        
        raise
    
    finally:
        db.close()


@celery_app.task(bind=True, name="analyze_all_user_keywords")
def analyze_all_user_keywords_task(self, user_id: int) -> Dict[str, Any]:
    """
    Celery task to analyze trends for all keywords belonging to a user.
    
    Args:
        user_id: ID of the user
        
    Returns:
        Dictionary containing analysis results for all keywords
    """
    task_id = self.request.id
    db = next(get_db())
    
    try:
        # Log task start
        process_log = ProcessLog(
            user_id=user_id,
            task_type="bulk_trend_analysis",
            status="running",
            task_id=task_id
        )
        db.add(process_log)
        db.commit()
        
        logger.info(f"Starting bulk trend analysis for user_id: {user_id}")
        
        # Get all user keywords
        keywords = db.query(Keyword).filter(
            Keyword.user_id == user_id,
            Keyword.is_active == True
        ).all()
        
        if not keywords:
            logger.warning(f"No active keywords found for user_id: {user_id}")
            return {"success": True, "message": "No active keywords to analyze", "results": []}
        
        total_keywords = len(keywords)
        results = []
        
        current_task.update_state(
            state='PROGRESS',
            meta={'current': 0, 'total': total_keywords, 'status': f'Analyzing {total_keywords} keywords...'}
        )
        
        # Analyze each keyword
        for i, keyword in enumerate(keywords):
            try:
                logger.info(f"Analyzing keyword: {keyword.keyword} ({i+1}/{total_keywords})")
                
                trend_data = trend_analysis_service.analyze_keyword_trends(keyword.id, db)
                
                results.append({
                    "keyword_id": keyword.id,
                    "keyword": keyword.keyword,
                    "success": True,
                    "trend_data": trend_data
                })
                
                # Update progress
                progress = int((i + 1) / total_keywords * 100)
                current_task.update_state(
                    state='PROGRESS',
                    meta={
                        'current': i + 1, 
                        'total': total_keywords, 
                        'status': f'Analyzed {keyword.keyword} ({i+1}/{total_keywords})'
                    }
                )
                
            except Exception as e:
                error_msg = f"Error analyzing keyword {keyword.keyword}: {str(e)}"
                logger.error(error_msg)
                
                results.append({
                    "keyword_id": keyword.id,
                    "keyword": keyword.keyword,
                    "success": False,
                    "error": error_msg
                })
        
        # Update process log with success
        process_log.status = "completed"
        process_log.completed_at = db.func.now()
        db.commit()
        
        successful_analyses = sum(1 for r in results if r["success"])
        
        current_task.update_state(
            state='SUCCESS',
            meta={
                'current': total_keywords, 
                'total': total_keywords, 
                'status': f'Completed: {successful_analyses}/{total_keywords} successful'
            }
        )
        
        logger.info(f"Bulk trend analysis completed for user_id: {user_id}. {successful_analyses}/{total_keywords} successful")
        
        return {
            "success": True,
            "user_id": user_id,
            "total_keywords": total_keywords,
            "successful_analyses": successful_analyses,
            "results": results,
            "task_id": task_id
        }
        
    except Exception as e:
        error_msg = f"Error in bulk trend analysis for user_id {user_id}: {str(e)}"
        logger.error(error_msg)
        
        # Update process log with error
        try:
            process_log.status = "failed"
            process_log.error_message = error_msg
            process_log.completed_at = db.func.now()
            db.commit()
        except:
            pass
        
        current_task.update_state(
            state='FAILURE',
            meta={'error': error_msg}
        )
        
        raise
    
    finally:
        db.close()


@celery_app.task(bind=True, name="calculate_keyword_importance_ranking")
def calculate_keyword_importance_ranking_task(self, user_id: int) -> Dict[str, Any]:
    """
    Celery task to calculate keyword importance ranking for a user.
    
    Args:
        user_id: ID of the user
        
    Returns:
        Dictionary containing keyword rankings
    """
    task_id = self.request.id
    db = next(get_db())
    
    try:
        logger.info(f"Calculating keyword importance ranking for user_id: {user_id}")
        
        current_task.update_state(
            state='PROGRESS',
            meta={'current': 50, 'total': 100, 'status': 'Calculating keyword rankings...'}
        )
        
        # Get keyword importance ranking
        rankings = trend_analysis_service.get_keyword_importance_ranking(user_id, db)
        
        current_task.update_state(
            state='SUCCESS',
            meta={'current': 100, 'total': 100, 'status': 'Rankings calculated successfully'}
        )
        
        logger.info(f"Keyword importance ranking completed for user_id: {user_id}")
        
        return {
            "success": True,
            "user_id": user_id,
            "rankings": rankings,
            "total_keywords": len(rankings),
            "task_id": task_id
        }
        
    except Exception as e:
        error_msg = f"Error calculating keyword importance ranking for user_id {user_id}: {str(e)}"
        logger.error(error_msg)
        
        current_task.update_state(
            state='FAILURE',
            meta={'error': error_msg}
        )
        
        raise
    
    finally:
        db.close()


@celery_app.task(bind=True, name="scheduled_trend_analysis")
def scheduled_trend_analysis_task(self) -> Dict[str, Any]:
    """
    Scheduled task to perform trend analysis for all active keywords.
    This task can be run periodically (e.g., daily) to keep trend data up to date.
    
    Returns:
        Dictionary containing analysis results
    """
    task_id = self.request.id
    db = next(get_db())
    
    try:
        logger.info("Starting scheduled trend analysis for all active keywords")
        
        # Get all active keywords
        active_keywords = db.query(Keyword).filter(Keyword.is_active == True).all()
        
        if not active_keywords:
            logger.info("No active keywords found for scheduled analysis")
            return {"success": True, "message": "No active keywords to analyze"}
        
        total_keywords = len(active_keywords)
        results = []
        
        current_task.update_state(
            state='PROGRESS',
            meta={'current': 0, 'total': total_keywords, 'status': f'Analyzing {total_keywords} keywords...'}
        )
        
        # Group keywords by user for batch processing
        user_keywords = {}
        for keyword in active_keywords:
            if keyword.user_id not in user_keywords:
                user_keywords[keyword.user_id] = []
            user_keywords[keyword.user_id].append(keyword)
        
        processed_count = 0
        
        # Process keywords by user
        for user_id, keywords in user_keywords.items():
            for keyword in keywords:
                try:
                    trend_data = trend_analysis_service.analyze_keyword_trends(keyword.id, db)
                    
                    results.append({
                        "keyword_id": keyword.id,
                        "keyword": keyword.keyword,
                        "user_id": user_id,
                        "success": True,
                        "trend_data": trend_data
                    })
                    
                except Exception as e:
                    error_msg = f"Error analyzing keyword {keyword.keyword}: {str(e)}"
                    logger.error(error_msg)
                    
                    results.append({
                        "keyword_id": keyword.id,
                        "keyword": keyword.keyword,
                        "user_id": user_id,
                        "success": False,
                        "error": error_msg
                    })
                
                processed_count += 1
                
                # Update progress
                current_task.update_state(
                    state='PROGRESS',
                    meta={
                        'current': processed_count,
                        'total': total_keywords,
                        'status': f'Processed {processed_count}/{total_keywords} keywords'
                    }
                )
        
        successful_analyses = sum(1 for r in results if r["success"])
        
        current_task.update_state(
            state='SUCCESS',
            meta={
                'current': total_keywords,
                'total': total_keywords,
                'status': f'Completed: {successful_analyses}/{total_keywords} successful'
            }
        )
        
        logger.info(f"Scheduled trend analysis completed. {successful_analyses}/{total_keywords} successful")
        
        return {
            "success": True,
            "total_keywords": total_keywords,
            "successful_analyses": successful_analyses,
            "results": results,
            "task_id": task_id
        }
        
    except Exception as e:
        error_msg = f"Error in scheduled trend analysis: {str(e)}"
        logger.error(error_msg)
        
        current_task.update_state(
            state='FAILURE',
            meta={'error': error_msg}
        )
        
        raise
    
    finally:
        db.close()