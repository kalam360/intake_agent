"""
API routes for the real estate intake agent.

This module provides FastAPI routes for handling text mode interactions
and mode switching between text and voice modes.
"""
import logging
import json
from typing import Dict, Any, List, Optional

from fastapi import APIRouter, HTTPException, Body, Depends
from pydantic import BaseModel

from ..text_agent import TextIntakeAgent

# Setup logging
logger = logging.getLogger("api-routes")

# Create router
router = APIRouter(prefix="/api/intake", tags=["intake"])

# In-memory store for agent instances
# In a production environment, you would use a database or Redis
agent_instances = {}

class TextMessage(BaseModel):
    """Model for text message requests."""
    message: str
    session_id: str
    agent_state: Optional[Dict[str, Any]] = None

class ModeSwitch(BaseModel):
    """Model for mode switching requests."""
    session_id: str
    current_mode: str
    new_mode: str
    agent_state: Optional[Dict[str, Any]] = None

class ConnectionDetails(BaseModel):
    """Model for LiveKit connection details."""
    url: str
    token: str

def get_or_create_text_agent(session_id: str, state: Optional[Dict[str, Any]] = None) -> TextIntakeAgent:
    """
    Get an existing text agent or create a new one.
    
    Args:
        session_id: The session ID
        state: Optional state to initialize the agent with
        
    Returns:
        A TextIntakeAgent instance
    """
    if session_id not in agent_instances:
        agent_instances[session_id] = TextIntakeAgent(imported_state=state)
    
    return agent_instances[session_id]

@router.post("/text-message")
async def process_text_message(data: TextMessage) -> Dict[str, Any]:
    """
    Process a text message and return a response.
    
    Args:
        data: The request data containing the message and session info
        
    Returns:
        Dictionary containing the response and updated state
    """
    try:
        # Get or create the text agent
        agent = get_or_create_text_agent(data.session_id, data.agent_state)
        
        # Process the message
        result = await agent.process_message(data.message)
        
        return {
            "response": result["response"],
            "client_data": result["client_data"],
            "state": result["state"]
        }
    except Exception as e:
        logger.error(f"Error processing text message: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/switch-mode")
async def switch_mode(data: ModeSwitch) -> Dict[str, Any]:
    """
    Handle switching between text and voice modes.
    
    Args:
        data: The request data containing mode switching info
        
    Returns:
        Dictionary containing updated state and connection details if needed
    """
    try:
        if data.current_mode == "text" and data.new_mode == "voice":
            # Switching from text to voice
            # Get the text agent state
            if data.session_id in agent_instances:
                text_agent = agent_instances[data.session_id]
                state = text_agent.export_state()
                
                # Generate LiveKit connection details
                # In a real implementation, you would generate a token for LiveKit
                connection_details = {
                    "url": "wss://your-livekit-server.com",
                    "token": "your-livekit-token",
                    "state": state
                }
                
                return {
                    "mode": "voice",
                    "connection_details": connection_details
                }
            else:
                # No existing text agent, create new voice connection
                connection_details = {
                    "url": "wss://your-livekit-server.com",
                    "token": "your-livekit-token"
                }
                
                return {
                    "mode": "voice",
                    "connection_details": connection_details
                }
        
        elif data.current_mode == "voice" and data.new_mode == "text":
            # Switching from voice to text
            # Create a new text agent with the imported state
            text_agent = get_or_create_text_agent(data.session_id, data.agent_state)
            
            # Generate a transition message
            transition_message = text_agent.get_transition_message()
            
            return {
                "mode": "text",
                "message": transition_message,
                "state": text_agent.export_state()
            }
        
        else:
            # Invalid mode switch
            raise HTTPException(status_code=400, detail="Invalid mode switch")
    
    except Exception as e:
        logger.error(f"Error switching modes: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/initial-greeting/{session_id}")
async def get_initial_greeting(session_id: str) -> Dict[str, Any]:
    """
    Get the initial greeting for a new session.
    
    Args:
        session_id: The session ID
        
    Returns:
        Dictionary containing the initial greeting and state
    """
    try:
        # Create a new text agent
        agent = get_or_create_text_agent(session_id)
        
        return {
            "greeting": agent.get_initial_greeting(),
            "state": agent.export_state()
        }
    except Exception as e:
        logger.error(f"Error getting initial greeting: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/cost-summary/{session_id}")
async def get_cost_summary(session_id: str) -> Dict[str, Any]:
    """
    Get a summary of the session costs.
    
    Args:
        session_id: The session ID
        
    Returns:
        Dictionary containing cost information
    """
    try:
        if session_id in agent_instances:
            agent = agent_instances[session_id]
            return agent.get_cost_summary()
        else:
            return {
                "total_cost": "$0.0000",
                "audio_seconds": "0.0s",
                "tokens": "0",
                "characters": "0"
            }
    except Exception as e:
        logger.error(f"Error getting cost summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))
