"""
Real Estate Intake Agent Prompts

This module contains the prompts and instructions for the real estate intake agent.
It defines the script structure, questions, and conversation flow for gathering
client information in a professional and efficient manner.
"""
from typing import Dict, List, Optional, TypedDict


class IntakeField(TypedDict):
    """Represents a field in the intake form with its description and possible follow-up questions."""
    name: str
    description: str
    follow_up: Optional[List[str]]


# Define the intake sections and their fields
INTAKE_SECTIONS: Dict[str, List[IntakeField]] = {
    "Contact Information": [
        {
            "name": "full_name",
            "description": "Full name",
            "follow_up": None
        },
        {
            "name": "email",
            "description": "Email address",
            "follow_up": None
        },
        {
            "name": "phone",
            "description": "Phone number",
            "follow_up": None
        },
        {
            "name": "preferred_contact",
            "description": "Preferred contact method (email, phone, text)",
            "follow_up": ["What's the best time to reach you?"]
        }
    ],
    "Property Goals": [
        {
            "name": "transaction_type",
            "description": "Are you looking to buy, sell, or rent a property?",
            "follow_up": ["Is this your first time buying/selling/renting?"]
        },
        {
            "name": "timeline",
            "description": "What's your timeline for moving in or completing the transaction?",
            "follow_up": ["Is there a specific reason for this timeline?"]
        },
        {
            "name": "budget",
            "description": "What's your budget or target price range?",
            "follow_up": ["How flexible are you with this budget?"]
        }
    ],
    "Search Criteria": [
        {
            "name": "location",
            "description": "What areas or neighborhoods are you interested in?",
            "follow_up": ["Are you open to considering other areas?"]
        },
        {
            "name": "bedrooms",
            "description": "How many bedrooms are you looking for?",
            "follow_up": None
        },
        {
            "name": "property_type",
            "description": "What type of property are you interested in? (house, condo, townhouse, etc.)",
            "follow_up": None
        },
        {
            "name": "must_haves",
            "description": "What features are must-haves for your new property?",
            "follow_up": ["Are there any deal-breakers we should know about?"]
        }
    ],
    "Financing": [
        {
            "name": "pre_approval",
            "description": "Have you been pre-approved for a mortgage?",
            "follow_up": ["Would you like a referral to a trusted mortgage broker?"]
        },
        {
            "name": "payment_method",
            "description": "Will you be paying with cash or financing with a loan?",
            "follow_up": None
        }
    ],
    "Additional Information": [
        {
            "name": "pets",
            "description": "Do you have any pets that will be living with you?",
            "follow_up": ["What type and how many?"]
        },
        {
            "name": "accessibility",
            "description": "Do you have any accessibility requirements?",
            "follow_up": None
        },
        {
            "name": "urgency",
            "description": "How urgent is your need to buy/sell/rent?",
            "follow_up": None
        },
        {
            "name": "additional_notes",
            "description": "Is there anything else you'd like us to know about your situation or requirements?",
            "follow_up": None
        }
    ]
}


# Agent instructions
AGENT_INSTRUCTIONS = """
You are a professional real estate intake agent for a high-quality real estate agency. 
Your job is to collect information from potential clients in a friendly, professional manner.

Follow these guidelines:
1. Introduce yourself briefly and explain the purpose of the conversation
2. Collect all required information in a conversational way
3. Ask follow-up questions when appropriate to get more detailed information
4. Validate the information provided and ask for clarification when needed
5. Before concluding, summarize the information collected and verify its accuracy
6. Be respectful of the client's time - keep the conversation efficient but thorough
7. Thank the client for their time at the end
8. Avoid discussing specific properties or giving advice - your role is information gathering only
9. If the client asks questions about the process, provide brief, helpful answers
10. Use a warm, professional tone throughout the conversation

Begin by introducing yourself and explaining that you'll be asking some questions to better understand 
their real estate needs. Then proceed through the intake sections in order.
"""


# Initial greeting
INITIAL_GREETING = """
Hello! I'm your real estate intake assistant. I'm here to gather some information about your real estate needs 
so we can match you with the right agent and properties. This will take just a few minutes of your time.

I'll be asking questions about your contact information, property goals, search criteria, and financing situation. 
Feel free to ask me any questions along the way. Shall we get started?
"""


# Validation prompt
VALIDATION_PROMPT = """
Thank you for providing that information. Let me make sure I have everything correctly:

{summary}

Is all of this information correct? If anything needs to be changed or if I've missed something, please let me know.
"""


# Clarification prompt
CLARIFICATION_PROMPT = """
I need to clarify a few details to make sure I have the most accurate information for our agents:

{clarification_questions}

Could you please help me fill in these details?
"""


# Closing message
CLOSING_MESSAGE = """
Thank you for providing all this information! This will be incredibly helpful in finding the right options for you.

One of our experienced real estate agents will reach out to you within 24 hours using your preferred contact method.
They'll have all the details you've shared with me and will be ready to help you with your {transaction_type} journey.

Is there anything else you'd like to add before we wrap up?
"""