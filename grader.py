from typing import List
from engine import SaaSSupportEnv
from models import ActionType, TicketStatus

class Grader:
    """
    Programmatic scoring logic for the SaaS Billing Environment tasks.
    Ensures scores are within the 0.0 - 1.0 range.
    """
    
    @staticmethod
    def grade_task_1(env: SaaSSupportEnv) -> float:
        """
        Easy: Email update with verification.
        - 1.0 if email updated correctly and ticket resolved.
        - 0.5 if verification was triggered but update not completed.
        - 0.0 otherwise.
        """
        history = env.action_history
        # Check if verification was mentioned in system messages
        verified = env.verification_pending or any("Security: Please verify" in msg.content for msg in env.current_ticket["history"])
        # Check if email in DB matches the target email in task_1
        updated = env.db.customers["cust_001"]["email"] == "alice_new@example.com"
        resolved = env.current_ticket["status"] == TicketStatus.RESOLVED

        if updated and resolved:
            return 1.0
        if verified:
            return 0.5
        return 0.0

    @staticmethod
    def grade_task_2(env: SaaSSupportEnv) -> float:
        """
        Medium: Pro-rated refund calculation.
        - 1.0 if correct amount ($14.99) refunded for inv_101.
        - 0.5 if refund issued but wrong amount.
        - 0.2 if billing lookup performed.
        - 0.0 otherwise.
        """
        history = env.action_history
        looked_up = any(a.action_type == ActionType.LOOKUP_BILLING for a in history)
        
        correct_refund = False
        any_refund = False
        for action in history:
            if action.action_type == ActionType.TRIGGER_REFUND:
                any_refund = True
                payload = action.payload
                # Check if invoice_id matches and amount is within 0.01 tolerance
                if payload.get("invoice_id") == "inv_101" and abs(float(payload.get("amount", 0)) - 14.99) < 0.01:
                    correct_refund = True
        
        if correct_refund:
            return 1.0
        if any_refund:
            return 0.5
        if looked_up:
            return 0.2
        return 0.0

    @staticmethod
    def grade_task_3(env: SaaSSupportEnv) -> float:
        """
        Hard: Retention & Escalation.
        - 1.0 if Loyalty Discount offered to Enterprise customer and no refund issued.
        - 0.5 if Loyalty Discount offered but refund also issued (policy violation).
        - 0.0 otherwise.
        """
        history = env.action_history
        loyalty_offered = any(a.action_type == ActionType.OFFER_LOYALTY_DISCOUNT for a in history)
        refund_issued = any(a.action_type == ActionType.TRIGGER_REFUND for a in history)

        if loyalty_offered and not refund_issued:
            return 1.0
        if loyalty_offered and refund_issued:
            return 0.5
        return 0.0
