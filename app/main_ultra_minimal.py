"""
Ultra minimal FastAPI application for Vercel deployment.
This version has absolutely no external dependencies except FastAPI and uvicorn.
"""

from fastapi import FastAPI
from datetime import datetime

# Create the most basic FastAPI app possible
app = FastAPI(
    title="Reddit Content Platform API - Ultra Minimal",
    version="1.0.0",
    description="Ultra minimal version for deployment testing"
)

@app.get("/")
async def root():
    """Root endpoint - most basic response possible."""
    return {
        "message": "Hello from Reddit Content Platform!",
        "status": "working",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "ultra-minimal-1.0.0"
    }

@app.get("/health")
async def health():
    """Basic health check."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/test")
async def test():
    """Test endpoint to verify deployment."""
    return {
        "test": "success",
        "message": "Deployment is working!",
        "timestamp": datetime.utcnow().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)