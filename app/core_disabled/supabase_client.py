"""
Supabase client configuration for additional services.
This complements the PostgreSQL database connection.
"""

import logging
from typing import Optional
import os

try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False
    Client = None

from app.core.config import settings

logger = logging.getLogger(__name__)


class SupabaseManager:
    """
    Manager for Supabase services including Auth, Storage, and Edge Functions.
    """
    
    def __init__(self):
        self._client: Optional[Client] = None
        self._initialized = False
    
    @property
    def client(self) -> Optional[Client]:
        """
        Get Supabase client instance.
        Returns None if Supabase is not configured or available.
        """
        if not self._initialized:
            self._initialize_client()
        return self._client
    
    def _initialize_client(self):
        """Initialize Supabase client if credentials are available."""
        self._initialized = True
        
        if not SUPABASE_AVAILABLE:
            logger.warning("Supabase Python client not installed. Install with: pip install supabase")
            return
        
        supabase_url = getattr(settings, 'SUPABASE_URL', None) or os.getenv('SUPABASE_URL')
        supabase_key = getattr(settings, 'SUPABASE_ANON_KEY', None) or os.getenv('SUPABASE_ANON_KEY')
        
        if not supabase_url or not supabase_key:
            logger.info("Supabase credentials not configured. Supabase services will be unavailable.")
            return
        
        try:
            self._client = create_client(supabase_url, supabase_key)
            logger.info("Supabase client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Supabase client: {e}")
    
    def is_available(self) -> bool:
        """Check if Supabase client is available and configured."""
        return self.client is not None
    
    def get_auth(self):
        """Get Supabase Auth client."""
        if not self.client:
            raise RuntimeError("Supabase client not available")
        return self.client.auth
    
    def get_storage(self):
        """Get Supabase Storage client."""
        if not self.client:
            raise RuntimeError("Supabase client not available")
        return self.client.storage
    
    def get_functions(self):
        """Get Supabase Edge Functions client."""
        if not self.client:
            raise RuntimeError("Supabase client not available")
        return self.client.functions
    
    async def health_check(self) -> dict:
        """
        Perform health check on Supabase services.
        """
        if not self.client:
            return {
                "status": "unavailable",
                "message": "Supabase client not configured"
            }
        
        try:
            # Simple health check by querying our users table
            response = self.client.table('users').select('id').limit(1).execute()
            return {
                "status": "healthy",
                "message": "Supabase connection successful",
                "response_time_ms": 0
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "message": f"Supabase connection failed: {str(e)}"
            }


# Global Supabase manager instance
supabase_manager = SupabaseManager()


def get_supabase_client() -> Optional[Client]:
    """
    Get the global Supabase client instance.
    Returns None if not configured.
    """
    return supabase_manager.client


def is_supabase_available() -> bool:
    """Check if Supabase is available and configured."""
    return supabase_manager.is_available()