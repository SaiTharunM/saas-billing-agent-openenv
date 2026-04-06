from enum import Enum
from typing import List, Dict, Any, Optional, Union
from pydantic import BaseModel, Field

class CustomerTier(str, Enum):
    """Tier of the customer subscription."""
    FREE = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"

class MessageRole(str, Enum):
    """Role of the message sender."""
    CUSTOMER = "customer"
    AGENT = "agent"
    SYSTEM = "system"

class TicketStatus(str, Enum):
    """Status of the support ticket."""
    OPEN = "open"
    PENDING = "pending"
    RESOLVED = "resolved"
    CLOSED = "closed"

class ActionType(str, Enum):
    """Available actions for the agent."""
    REPLY = "reply"
    LOOKUP_BILLING = "lookup_billing"
    TRIGGER_REFUND = "trigger_refund"
    UPDATE_SUBSCRIPTION = "update_subscription"
    CLOSE_TICKET = "close_ticket"
    UPDATE_CUSTOMER_RECORD = "update_customer_record"
    OFFER_RETENTION_CREDIT = "offer_retention_credit"
    OFFER_LOYALTY_DISCOUNT = "offer_loyalty_discount"

class ChatMessage(BaseModel):
    """A single message in the chat history."""
    role: MessageRole
    content: str

class CustomerInfo(BaseModel):
    """Metadata about the customer."""
    name: str
    tier: CustomerTier

class Observation(BaseModel):
    """The state of the environment as seen by the agent."""
    ticket_id: str
    customer_info: CustomerInfo
    last_message: str
    chat_history: List[ChatMessage] = Field(default_factory=list)
    available_tools: List[str] = Field(default_factory=list)
    current_status: TicketStatus

class Action(BaseModel):
    """An action taken by the agent."""
    action_type: ActionType
    payload: Dict[str, Any] = Field(default_factory=dict)

class Reward(BaseModel):
    """The reward and termination status after an action."""
    value: float
    reason: str
    is_terminal: bool
