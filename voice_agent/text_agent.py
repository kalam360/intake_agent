"""
Text-based real estate intake agent implementation.

This module provides a text-based agent that uses OpenAI's API directly
for processing user messages and generating responses.
"""
import logging
import json
from typing import Dict, Any, List, Optional, Tuple

import openai
from dotenv import load_dotenv

from .base_agent import BaseIntakeAgent
from intake_core import (
    AGENT_INSTRUCTIONS,
    INITIAL_GREETING,
    CLOSING_MESSAGE,
    VALIDATION_PROMPT,
    CLARIFICATION_PROMPT,
    tracker,
    track_llm
)

logger = logging.getLogger("text-intake-agent")

class TextIntakeAgent(BaseIntakeAgent):
    """
    Text-based real estate intake agent.
    
    This agent uses OpenAI's API directly to process text messages
    and generate responses, following the same intake flow as the voice agent.
    """
    
    def __init__(self, imported_state: Optional[Dict[str, Any]] = None):
        """
        Initialize the text agent.
        
        Args:
            imported_state: Optional state to import from another agent
        """
        super().__init__()
        self.system_prompt = AGENT_INSTRUCTIONS
        
        # Import state if provided (for mode switching)
        if imported_state:
            self.import_state(imported_state)
            
        # If we're just starting, add the initial greeting to the conversation history
        if not self.conversation_history:
            self.conversation_history.append({
                "role": "assistant",
                "content": INITIAL_GREETING
            })
    
    @track_llm("gpt-4o-mini")
    async def process_message(self, message: str) -> Dict[str, Any]:
        """
        Process a text message from the user.
        
        Args:
            message: The user's message
            
        Returns:
            Dictionary containing the response and updated state
        """
        # Add to conversation history
        self.conversation_history.append({
            "role": "user",
            "content": message
        })
        
        # Extract information from message
        # For text mode, we'll use a simple context dictionary with the message
        context = {"message": message}
        self.update_client_data(context)
        
        # Check if we need to validate
        if len(self.client_data) >= 3 and not self.validation_in_progress and not self.intake_complete:
            validation_result = self.validate_intake_information()
            
            if validation_result["valid"]:
                # If validation passes, ask for confirmation
                response = VALIDATION_PROMPT.format(summary=validation_result["summary"])
                self.current_stage = "confirmation"
            else:
                # If validation fails, ask clarification questions
                clarification_text = "\n".join([f"- {q}" for q in validation_result["questions"]])
                response = CLARIFICATION_PROMPT.format(clarification_questions=clarification_text)
                self.current_stage = "clarification"
        else:
            # Generate response using OpenAI
            response = await self.generate_response(message)
            
            # Check for confirmation of validation
            if self.validation_in_progress:
                if any(confirm in message.lower() for confirm in ["yes", "correct", "that's right", "looks good"]):
                    self.intake_complete = True
                    transaction_type = self.client_data.get("transaction_type", "real estate")
                    response = CLOSING_MESSAGE.format(transaction_type=transaction_type)
                    self.current_stage = "completed"
                else:
                    # If they didn't confirm, continue the conversation
                    self.validation_in_progress = False
                    self.current_stage = "gathering"
        
        # Add to conversation history
        self.conversation_history.append({
            "role": "assistant",
            "content": response
        })
        
        return {
            "response": response,
            "client_data": self.client_data,
            "state": self.export_state()
        }
    
    async def generate_response(self, user_message: str) -> str:
        """
        Generate a response using OpenAI's API.
        
        Args:
            user_message: The user's message
            
        Returns:
            The generated response
        """
        # Prepare the messages for the API call
        messages = [
            {"role": "system", "content": self.system_prompt}
        ]
        
        # Add conversation history (limited to last 10 messages to keep context manageable)
        for message in self.conversation_history[-10:]:
            messages.append(message)
        
        try:
            # Call the OpenAI API
            response = await openai.ChatCompletion.acreate(
                model="gpt-4o-mini",
                messages=messages,
                temperature=0.7,
                max_tokens=500
            )
            
            # Extract and return the response text
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return "I'm sorry, I encountered an error processing your request. Please try again."
    
    def get_initial_greeting(self) -> str:
        """
        Get the initial greeting message.
        
        Returns:
            The initial greeting message
        """
        return INITIAL_GREETING
    
    def get_cost_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the session costs.
        
        Returns:
            Dictionary containing cost information
        """
        summary = tracker.get_usage_summary()
        
        return {
            "total_cost": f"${summary['total_cost']:.4f}",
            "audio_seconds": f"{summary['total_audio_seconds']:.1f}s",
            "tokens": f"{summary['total_input_tokens'] + summary['total_output_tokens']}",
            "characters": f"{summary['total_characters']}"
        }
