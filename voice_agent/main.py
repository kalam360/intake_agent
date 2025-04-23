"""
Main FastAPI application for the real estate intake agent.

This module provides the FastAPI application that integrates both
text and voice modes for the real estate intake agent.
"""
import logging
import os
from pathlib import Path

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from api import router as intake_router

# Load environment variables
load_dotenv(Path(__file__).with_name(".env.local"), override=True)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("intake_api.log")
    ]
)
logger = logging.getLogger("intake-api")

# Create FastAPI app
app = FastAPI(
    title="Real Estate Intake Agent API",
    description="API for the real estate intake agent with text and voice modes",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(intake_router)

@app.get("/")
async def root():
    """Root endpoint for health check."""
    return {"status": "ok", "message": "Real Estate Intake Agent API is running"}

if __name__ == "__main__":
    # Get port from environment variable or use default
    port = int(os.environ.get("PORT", 8000))
    
    # Run the FastAPI app with uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=True
    )
