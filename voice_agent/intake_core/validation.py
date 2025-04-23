"""
Validation module for real estate intake information.

This module provides functions to validate and verify the information
collected during the intake process, ensuring completeness and correctness.
"""
from typing import Dict, List, Optional, Tuple, Any
import re
from datetime import datetime, timedelta

# Email validation regex pattern
EMAIL_PATTERN = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"

# Phone validation regex pattern (simple version)
PHONE_PATTERN = r"^\+?[0-9]{10,15}$"


def validate_contact_info(data: Dict[str, Any]) -> List[str]:
    """
    Validate contact information fields.
    
    Args:
        data: Dictionary containing contact information
        
    Returns:
        List of validation issues, empty if all valid
    """
    issues = []
    
    # Check name
    if not data.get("full_name"):
        issues.append("Full name is missing")
    elif len(data.get("full_name", "")) < 3:
        issues.append("Full name seems too short")
    
    # Check email
    if not data.get("email"):
        issues.append("Email address is missing")
    elif not re.match(EMAIL_PATTERN, data.get("email", "")):
        issues.append("Email address format appears invalid")
    
    # Check phone
    if not data.get("phone"):
        issues.append("Phone number is missing")
    elif not re.match(PHONE_PATTERN, data.get("phone", "")):
        issues.append("Phone number format appears invalid")
    
    # Check preferred contact method
    if not data.get("preferred_contact"):
        issues.append("Preferred contact method is missing")
    elif data.get("preferred_contact", "").lower() not in ["email", "phone", "text"]:
        issues.append("Preferred contact method should be email, phone, or text")
    
    return issues


def validate_property_goals(data: Dict[str, Any]) -> List[str]:
    """
    Validate property goals information.
    
    Args:
        data: Dictionary containing property goals information
        
    Returns:
        List of validation issues, empty if all valid
    """
    issues = []
    
    # Check transaction type
    if not data.get("transaction_type"):
        issues.append("Transaction type (buy/sell/rent) is missing")
    elif data.get("transaction_type", "").lower() not in ["buy", "sell", "rent"]:
        issues.append("Transaction type should be buy, sell, or rent")
    
    # Check timeline
    if not data.get("timeline"):
        issues.append("Timeline information is missing")
    else:
        # Try to interpret timeline
        timeline = data.get("timeline", "").lower()
        has_timeframe = any(term in timeline for term in [
            "day", "week", "month", "year", "asap", "soon", "immediately"
        ])
        if not has_timeframe:
            issues.append("Timeline information needs clarification with a timeframe")
    
    # Check budget
    if not data.get("budget"):
        issues.append("Budget or target price information is missing")
    
    return issues


def validate_search_criteria(data: Dict[str, Any]) -> List[str]:
    """
    Validate search criteria information.
    
    Args:
        data: Dictionary containing search criteria
        
    Returns:
        List of validation issues, empty if all valid
    """
    issues = []
    
    # Only validate if transaction type is buy or rent
    transaction_type = data.get("transaction_type", "").lower()
    if transaction_type in ["buy", "rent"]:
        # Check location
        if not data.get("location"):
            issues.append("Location preference is missing")
        
        # Check bedrooms
        if not data.get("bedrooms"):
            issues.append("Number of bedrooms preference is missing")
        
        # Check property type
        if not data.get("property_type"):
            issues.append("Property type preference is missing")
    
    return issues


def validate_financing(data: Dict[str, Any]) -> List[str]:
    """
    Validate financing information.
    
    Args:
        data: Dictionary containing financing information
        
    Returns:
        List of validation issues, empty if all valid
    """
    issues = []
    
    # Only validate if transaction type is buy
    transaction_type = data.get("transaction_type", "").lower()
    if transaction_type == "buy":
        # Check pre-approval
        if "pre_approval" not in data:
            issues.append("Pre-approval status is missing")
        
        # Check payment method
        if not data.get("payment_method"):
            issues.append("Payment method (cash/loan) is missing")
        elif data.get("payment_method", "").lower() not in ["cash", "loan", "mortgage", "financing"]:
            issues.append("Payment method should indicate cash or some form of financing/loan")
    
    return issues


def validate_all(data: Dict[str, Any]) -> Dict[str, List[str]]:
    """
    Validate all intake information.
    
    Args:
        data: Dictionary containing all intake information
        
    Returns:
        Dictionary mapping section names to lists of validation issues
    """
    validation_results = {}
    
    # Validate contact information
    contact_issues = validate_contact_info(data)
    if contact_issues:
        validation_results["Contact Information"] = contact_issues
    
    # Validate property goals
    goals_issues = validate_property_goals(data)
    if goals_issues:
        validation_results["Property Goals"] = goals_issues
    
    # Validate search criteria
    criteria_issues = validate_search_criteria(data)
    if criteria_issues:
        validation_results["Search Criteria"] = criteria_issues
    
    # Validate financing
    financing_issues = validate_financing(data)
    if financing_issues:
        validation_results["Financing"] = financing_issues
    
    return validation_results


def generate_clarification_questions(validation_results: Dict[str, List[str]]) -> List[str]:
    """
    Generate clarification questions based on validation issues.
    
    Args:
        validation_results: Dictionary mapping section names to lists of validation issues
        
    Returns:
        List of clarification questions to ask the user
    """
    questions = []
    
    for section, issues in validation_results.items():
        for issue in issues:
            if "missing" in issue.lower():
                field = issue.split(" is ")[0].lower()
                questions.append(f"I don't think I caught your {field}. Could you please provide that information?")
            elif "invalid" in issue.lower() or "format" in issue.lower():
                field = issue.split(" format")[0].lower()
                questions.append(f"The {field} you provided doesn't seem to be in the right format. Could you please verify it?")
            elif "clarification" in issue.lower():
                field = issue.split(" needs ")[0].lower()
                questions.append(f"Could you please provide more specific details about your {field}?")
            else:
                # Generic clarification for other issues
                questions.append(f"Regarding {section.lower()}, {issue.lower()}. Could you please clarify?")
    
    return questions


def summarize_intake_data(data: Dict[str, Any]) -> str:
    """
    Generate a summary of the collected intake data.
    
    Args:
        data: Dictionary containing all intake information
        
    Returns:
        Formatted string summarizing the intake information
    """
    summary = "Here's a summary of the information you've provided:\n\n"
    
    # Contact Information
    summary += "Contact Information:\n"
    if data.get("full_name"):
        summary += f"- Name: {data.get('full_name')}\n"
    if data.get("email"):
        summary += f"- Email: {data.get('email')}\n"
    if data.get("phone"):
        summary += f"- Phone: {data.get('phone')}\n"
    if data.get("preferred_contact"):
        summary += f"- Preferred Contact Method: {data.get('preferred_contact')}\n"
    
    summary += "\n"
    
    # Property Goals
    summary += "Property Goals:\n"
    if data.get("transaction_type"):
        summary += f"- Transaction Type: {data.get('transaction_type')}\n"
    if data.get("timeline"):
        summary += f"- Timeline: {data.get('timeline')}\n"
    if data.get("budget"):
        summary += f"- Budget/Target Price: {data.get('budget')}\n"
    
    summary += "\n"
    
    # Search Criteria (only if buying or renting)
    transaction_type = data.get("transaction_type", "").lower()
    if transaction_type in ["buy", "rent"]:
        summary += "Search Criteria:\n"
        if data.get("location"):
            summary += f"- Location: {data.get('location')}\n"
        if data.get("bedrooms"):
            summary += f"- Bedrooms: {data.get('bedrooms')}\n"
        if data.get("property_type"):
            summary += f"- Property Type: {data.get('property_type')}\n"
        if data.get("must_haves"):
            summary += f"- Must-Have Features: {data.get('must_haves')}\n"
        
        summary += "\n"
    
    # Financing (only if buying)
    if transaction_type == "buy":
        summary += "Financing:\n"
        if "pre_approval" in data:
            pre_approval = "Yes" if data.get("pre_approval") else "No"
            summary += f"- Pre-Approved: {pre_approval}\n"
        if data.get("payment_method"):
            summary += f"- Payment Method: {data.get('payment_method')}\n"
        
        summary += "\n"
    
    # Additional Information
    summary += "Additional Information:\n"
    if data.get("pets"):
        summary += f"- Pets: {data.get('pets')}\n"
    if data.get("accessibility"):
        summary += f"- Accessibility Requirements: {data.get('accessibility')}\n"
    if data.get("urgency"):
        summary += f"- Urgency Level: {data.get('urgency')}\n"
    if data.get("additional_notes"):
        summary += f"- Additional Notes: {data.get('additional_notes')}\n"
    
    return summary