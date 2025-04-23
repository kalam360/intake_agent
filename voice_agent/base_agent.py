"""
Base agent implementation for real estate intake agents.

This module provides a common interface for both text and voice agents,
ensuring consistent behavior and state management across different modes.
"""
from typing import Dict, Any, List, Optional
import logging

from intake_core import (
    validate_all,
    generate_clarification_questions,
    summarize_intake_data
)

logger = logging.getLogger("base-intake-agent")

class BaseIntakeAgent:
    """
    Base class for real estate intake agents.
    
    This class defines the common interface and functionality for both
    text and voice agents, allowing for seamless mode switching.
    """
    
    def __init__(self):
        """Initialize the base agent with empty state."""
        # Initialize client data dictionary to store intake information
        self.client_data: Dict[str, Any] = {}
        # Track conversation state
        self.intake_complete = False
        self.validation_in_progress = False
        # Store conversation history
        self.conversation_history: List[Dict[str, str]] = []
        # Current stage in the intake process
        self.current_stage = "greeting"
    
    def export_state(self) -> Dict[str, Any]:
        """
        Export the current agent state for mode switching.
        
        Returns:
            Dictionary containing the current agent state
        """
        return {
            "client_data": self.client_data,
            "intake_complete": self.intake_complete,
            "validation_in_progress": self.validation_in_progress,
            "conversation_history": self.conversation_history,
            "current_stage": self.current_stage
        }
    
    def import_state(self, state: Dict[str, Any]):
        """
        Import state from another agent instance.
        
        Args:
            state: Dictionary containing the state to import
        """
        self.client_data = state.get("client_data", {})
        self.intake_complete = state.get("intake_complete", False)
        self.validation_in_progress = state.get("validation_in_progress", False)
        self.conversation_history = state.get("conversation_history", [])
        self.current_stage = state.get("current_stage", "greeting")
        
        logger.info(f"Imported state with {len(self.client_data)} client data fields")
        logger.info(f"Current stage: {self.current_stage}")
    
    def update_client_data(self, context: Dict[str, Any]):
        """
        Extract client data from the conversation context.
        
        Args:
            context: Dictionary containing context information
        """
        # Contact Information
        if context.get("name") or context.get("full_name"):
            self.client_data["full_name"] = context.get("name") or context.get("full_name")
        
        if context.get("email"):
            self.client_data["email"] = context.get("email")
        
        if context.get("phone") or context.get("phone_number"):
            self.client_data["phone"] = context.get("phone") or context.get("phone_number")
        
        if context.get("preferred_contact"):
            self.client_data["preferred_contact"] = context.get("preferred_contact")
        
        # Property Goals
        if context.get("transaction_type"):
            self.client_data["transaction_type"] = context.get("transaction_type")
        elif any(term in str(context).lower() for term in ["buy", "purchase"]):
            self.client_data["transaction_type"] = "buy"
        elif "sell" in str(context).lower():
            self.client_data["transaction_type"] = "sell"
        elif "rent" in str(context).lower():
            self.client_data["transaction_type"] = "rent"
        
        if context.get("timeline"):
            self.client_data["timeline"] = context.get("timeline")
        
        if context.get("budget") or context.get("price_range"):
            self.client_data["budget"] = context.get("budget") or context.get("price_range")
        
        # Search Criteria
        if context.get("location") or context.get("area") or context.get("neighborhood"):
            self.client_data["location"] = context.get("location") or context.get("area") or context.get("neighborhood")
        
        if context.get("bedrooms"):
            self.client_data["bedrooms"] = context.get("bedrooms")
        
        if context.get("property_type"):
            self.client_data["property_type"] = context.get("property_type")
        
        if context.get("must_haves") or context.get("requirements"):
            self.client_data["must_haves"] = context.get("must_haves") or context.get("requirements")
        
        # Financing
        if context.get("pre_approval") is not None:
            self.client_data["pre_approval"] = context.get("pre_approval")
        elif "pre-approved" in str(context).lower():
            self.client_data["pre_approval"] = True
        
        if context.get("payment_method"):
            self.client_data["payment_method"] = context.get("payment_method")
        elif "cash" in str(context).lower():
            self.client_data["payment_method"] = "cash"
        elif any(term in str(context).lower() for term in ["loan", "mortgage", "financing"]):
            self.client_data["payment_method"] = "loan"
        
        # Additional Information
        if context.get("pets"):
            self.client_data["pets"] = context.get("pets")
        
        if context.get("accessibility"):
            self.client_data["accessibility"] = context.get("accessibility")
        
        if context.get("urgency"):
            self.client_data["urgency"] = context.get("urgency")
        
        if context.get("additional_notes") or context.get("notes"):
            self.client_data["additional_notes"] = context.get("additional_notes") or context.get("notes")
    
    def validate_intake_information(self) -> Dict[str, Any]:
        """
        Validate the collected intake information.
        
        Returns:
            Dictionary containing validation results and next steps
        """
        # Validate the collected data
        validation_results = validate_all(self.client_data)
        
        if validation_results:
            # If there are validation issues, generate clarification questions
            clarification_questions = generate_clarification_questions(validation_results)
            return {
                "valid": False,
                "questions": clarification_questions,
                "next_stage": "clarification"
            }
        else:
            # If validation passes, summarize the data
            summary = summarize_intake_data(self.client_data)
            self.validation_in_progress = True
            
            return {
                "valid": True,
                "summary": summary,
                "next_stage": "confirmation"
            }
    
    def get_transition_message(self) -> str:
        """
        Generate a transition message when switching modes.
        
        Returns:
            A message acknowledging the mode switch and continuing the conversation
        """
        # If we have client data, acknowledge what we know
        if self.client_data:
            if "full_name" in self.client_data:
                intro = f"Thanks {self.client_data['full_name']}! "
            else:
                intro = "Thanks for the information so far! "
            
            # Mention what stage we're at
            if self.current_stage == "greeting":
                return f"{intro}Let's start gathering your real estate needs."
            elif self.validation_in_progress:
                return f"{intro}I was just reviewing the information you've provided. Let's continue with that."
            elif self.intake_complete:
                return f"{intro}We've completed the intake process. Is there anything else you'd like to add?"
            else:
                # Count how many sections we have data for
                sections_with_data = 0
                if any(field in self.client_data for field in ["full_name", "email", "phone"]):
                    sections_with_data += 1
                if any(field in self.client_data for field in ["transaction_type", "timeline", "budget"]):
                    sections_with_data += 1
                if any(field in self.client_data for field in ["location", "bedrooms", "property_type"]):
                    sections_with_data += 1
                
                if sections_with_data == 0:
                    return f"{intro}Let's start gathering your real estate needs."
                elif sections_with_data == 1:
                    return f"{intro}We've started gathering your information. Let's continue with more details about your real estate needs."
                else:
                    return f"{intro}We've made good progress. Let's continue gathering the remaining details about your real estate needs."
        else:
            # No data yet
            return "I'm here to help with your real estate needs. Let's get started!"
