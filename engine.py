import datetime
import random
from typing import List, Dict, Any, Optional, Union, Tuple
from models import (
    CustomerTier, MessageRole, TicketStatus, ActionType, 
    ChatMessage, CustomerInfo, Observation, Action, Reward
)

class CompanyPolicy:
    """
    The 'Bible' of rules the agent must follow.
    """
    REFUND_WINDOW_DAYS = 30
    PRO_RATED_REFUND_ALLOWED = True
    MAX_RETENTION_CREDIT_MONTHS = 1
    LOYALTY_DISCOUNT_PERCENT = 20
    EMAIL_VERIFICATION_REQUIRED = True

    @staticmethod
    def get_policy_text() -> str:
        """Returns the policy text for the agent to reason against."""
        return """
        Company Policy:
        1. Refunds: Only allowed within 30 days of the invoice date.
        2. Pro-rated Refunds: Allowed for mid-cycle cancellations. Calculate as (remaining days / total days) * invoice amount.
        3. Retention: Offer 1 month credit for churn risk.
        4. Loyalty: For Enterprise customers or high-value churn, offer a 20% Loyalty Discount.
        5. Security: Email updates require a verification step.
        """

class MockDatabase:
    """
    Stateful database that persists changes.
    """
    def __init__(self):
        """Initializes the mock database with synthetic customer data."""
        self.customers = {
            "cust_001": {
                "name": "Alice Smith",
                "email": "alice@example.com",
                "tier": CustomerTier.PRO,
                "subscription_date": datetime.datetime.now() - datetime.timedelta(days=15),
                "billing_history": [
                    {
                        "id": "inv_101", 
                        "date": (datetime.datetime.now() - datetime.timedelta(days=15)).strftime("%Y-%m-%d"), 
                        "amount": 29.99, 
                        "status": "paid", 
                        "period_start": (datetime.datetime.now() - datetime.timedelta(days=15)).strftime("%Y-%m-%d"), 
                        "period_end": (datetime.datetime.now() + datetime.timedelta(days=15)).strftime("%Y-%m-%d")
                    }
                ],
                "usage_logs": ["Login: 2024-03-01", "Export Data: 2024-03-05"],
                "verified": True
            },
            "cust_002": {
                "name": "Enterprise Corp",
                "email": "admin@enterprise.com",
                "tier": CustomerTier.ENTERPRISE,
                "subscription_date": datetime.datetime.now() - datetime.timedelta(days=400),
                "billing_history": [
                    {
                        "id": "inv_501", 
                        "date": (datetime.datetime.now() - datetime.timedelta(days=5)).strftime("%Y-%m-%d"), 
                        "amount": 499.99, 
                        "status": "paid", 
                        "period_start": (datetime.datetime.now() - datetime.timedelta(days=5)).strftime("%Y-%m-%d"), 
                        "period_end": (datetime.datetime.now() + datetime.timedelta(days=25)).strftime("%Y-%m-%d")
                    }
                ],
                "usage_logs": ["API Call: 10k/day", "User Added: 50"],
                "verified": True
            }
        }

    def update_email(self, customer_id: str, new_email: str) -> bool:
        """Updates the customer's email address in the database."""
        if customer_id in self.customers:
            self.customers[customer_id]["email"] = new_email
            return True
        return False

    def issue_refund(self, customer_id: str, invoice_id: str, amount: float) -> bool:
        """Issues a refund for a specific invoice in the database."""
        if customer_id in self.customers:
            for inv in self.customers[customer_id]["billing_history"]:
                if inv["id"] == invoice_id:
                    inv["status"] = "refunded"
                    inv["refund_amount"] = amount
                    return True
        return False

class SaaSSupportEnv:
    """
    The core OpenEnv engine for SaaS Billing Support.
    """
    def __init__(self):
        """Initializes the environment with a mock database and company policy."""
        self.db = MockDatabase()
        self.policy = CompanyPolicy()
        self.current_ticket = None
        self.current_customer_id = None
        self.is_terminal = False
        self.steps_taken = 0
        self.action_history = []
        self.task_difficulty = "easy"
        self.verification_pending = False

    def reset(self, ticket_id: str, customer_id: str, initial_message: str, difficulty: str = "easy") -> Observation:
        """Resets the environment for a new task."""
        self.current_customer_id = customer_id
        self.task_difficulty = difficulty
        self.current_ticket = {
            "id": ticket_id,
            "customer_id": customer_id,
            "last_message": initial_message,
            "history": [ChatMessage(role=MessageRole.CUSTOMER, content=initial_message)],
            "status": TicketStatus.OPEN
        }
        self.is_terminal = False
        self.steps_taken = 0
        self.action_history = []
        self.verification_pending = False
        return self._get_observation()

    def _get_observation(self) -> Observation:
        """Internal method to construct the current observation."""
        customer = self.db.customers[self.current_customer_id]
        return Observation(
            ticket_id=self.current_ticket["id"],
            customer_info=CustomerInfo(name=customer["name"], tier=customer["tier"]),
            last_message=self.current_ticket["last_message"],
            chat_history=self.current_ticket["history"],
            available_tools=[a.value for a in ActionType],
            current_status=self.current_ticket["status"]
        )

    def step(self, action: Action) -> Tuple[Observation, Reward]:
        """Executes an action in the environment and returns the next observation and reward."""
        if self.is_terminal:
            raise RuntimeError("Environment is terminal.")

        self.steps_taken += 1
        self.action_history.append(action)
        success = False
        info_msg = ""

        # Reward Shaping Logic
        step_reward = -0.05 # Time penalty

        if action.action_type == ActionType.LOOKUP_BILLING:
            step_reward += 0.1
            billing = self.db.customers[self.current_customer_id]["billing_history"]
            info_msg = f"Billing Records: {billing}. {self.policy.get_policy_text()}"
            success = True

        elif action.action_type == ActionType.UPDATE_CUSTOMER_RECORD:
            field = action.payload.get("field")
            value = action.payload.get("value")
            if field == "email":
                if self.verification_pending:
                    self.db.update_email(self.current_customer_id, value)
                    info_msg = "Email updated successfully after verification."
                    success = True
                    self.verification_pending = False
                else:
                    info_msg = "Security: Please verify the identity first."
                    self.verification_pending = True
                    success = False

        elif action.action_type == ActionType.TRIGGER_REFUND:
            inv_id = action.payload.get("invoice_id")
            amount = action.payload.get("amount", 0.0)
            
            # Hallucination Check
            valid_ids = [inv["id"] for inv in self.db.customers[self.current_customer_id]["billing_history"]]
            if inv_id not in valid_ids:
                step_reward -= 0.5
                info_msg = f"Error: Invoice {inv_id} not found."
                success = False
            else:
                # Policy Check
                inv = next(i for i in self.db.customers[self.current_customer_id]["billing_history"] if i["id"] == inv_id)
                inv_date = datetime.datetime.strptime(inv["date"], "%Y-%m-%d")
                if (datetime.datetime.now() - inv_date).days <= self.policy.REFUND_WINDOW_DAYS:
                    self.db.issue_refund(self.current_customer_id, inv_id, amount)
                    info_msg = f"Refund of {amount} issued for {inv_id}."
                    success = True
                else:
                    info_msg = "Refund rejected by Policy: Outside 30-day window."
                    success = False

        elif action.action_type == ActionType.OFFER_LOYALTY_DISCOUNT:
            if self.db.customers[self.current_customer_id]["tier"] == CustomerTier.ENTERPRISE:
                info_msg = "Loyalty discount applied to Enterprise account."
                success = True
            else:
                info_msg = "Loyalty discount only available for Enterprise tier."
                success = False

        elif action.action_type == ActionType.REPLY:
            # Stochastic Customer Behavior
            response = self._simulate_customer_response(action.payload.get("message", ""))
            self.current_ticket["history"].append(ChatMessage(role=MessageRole.AGENT, content=action.payload.get("message", "")))
            self.current_ticket["history"].append(ChatMessage(role=MessageRole.CUSTOMER, content=response))
            self.current_ticket["last_message"] = response
            success = True

        elif action.action_type == ActionType.CLOSE_TICKET:
            self.current_ticket["status"] = TicketStatus.RESOLVED
            self.is_terminal = True
            success = True

        if info_msg:
            self.current_ticket["history"].append(ChatMessage(role=MessageRole.SYSTEM, content=info_msg))

        reward_val = step_reward
        if self.is_terminal and success:
            reward_val += 1.0 # Full success bonus

        return self._get_observation(), Reward(value=reward_val, reason=info_msg or "Action processed.", is_terminal=self.is_terminal)

    def _simulate_customer_response(self, agent_msg: str) -> str:
        """Internal method to simulate customer responses based on difficulty."""
        if self.task_difficulty == "easy":
            return "Thank you, that sounds good. Please proceed."
        elif self.task_difficulty == "medium":
            return "I see. Can you explain how you calculated that amount?"
        else: # Hard
            responses = [
                "This is unacceptable! I've been a loyal customer for years.",
                "I don't have time for this. Just fix it or I'm canceling.",
                "Why is this so complicated? I just want my money back."
            ]
            return random.choice(responses)

    def state(self) -> Dict[str, Any]:
        """Returns the full internal state of the environment."""
        return {
            "db": self.db.customers,
            "ticket": self.current_ticket,
            "steps": self.steps_taken,
            "terminal": self.is_terminal
        }
