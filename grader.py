from typing import List
from engine import SaaSSupportEnv
from models import ActionType, TicketStatus


class Grader:
    """
    Programmatic scoring logic for the SaaS Billing Environment tasks.
    Ensures scores are strictly within (0, 1).
    """

    # ✅ COMMON SAFE NORMALIZER
    @staticmethod
    def normalize_score(score) -> float:
        try:
            score = float(score)
        except:
            return 0.5

        if score is None:
            return 0.5

        # ✅ STRICT RANGE (never 0 or 1)
        if score <= 0.0:
            return 0.01
        if score >= 1.0:
            return 0.99

        return score

    @staticmethod
    def grade_task_1(env: SaaSSupportEnv) -> float:
        history = env.action_history

        verified = env.verification_pending or any(
            "Security: Please verify" in msg.content
            for msg in env.current_ticket["history"]
        )

        updated = (
            env.db.customers["cust_001"]["email"]
            == "alice_new@example.com"
        )

        resolved = (
            env.current_ticket["status"] == TicketStatus.RESOLVED
        )

        if updated and resolved:
            score = 1.0
        elif verified:
            score = 0.5
        else:
            score = 0.0

        return Grader.normalize_score(score)  # ✅ FIX

    @staticmethod
    def grade_task_2(env: SaaSSupportEnv) -> float:
        history = env.action_history

        looked_up = any(
            a.action_type == ActionType.LOOKUP_BILLING
            for a in history
        )

        correct_refund = False
        any_refund = False

        for action in history:
            if action.action_type == ActionType.TRIGGER_REFUND:
                any_refund = True
                payload = action.payload

                try:
                    amount = float(payload.get("amount", 0))
                except:
                    amount = 0

                if (
                    payload.get("invoice_id") == "inv_101"
                    and abs(amount - 14.99) < 0.01
                ):
                    correct_refund = True

        if correct_refund:
            score = 1.0
        elif any_refund:
            score = 0.5
        elif looked_up:
            score = 0.2
        else:
            score = 0.0

        return Grader.normalize_score(score)  # ✅ FIX

    @staticmethod
    def grade_task_3(env: SaaSSupportEnv) -> float:
        history = env.action_history

        loyalty_offered = any(
            a.action_type == ActionType.OFFER_LOYALTY_DISCOUNT
            for a in history
        )

        refund_issued = any(
            a.action_type == ActionType.TRIGGER_REFUND
            for a in history
        )

        if loyalty_offered and not refund_issued:
            score = 1.0
        elif loyalty_offered and refund_issued:
            score = 0.5
        else:
            score = 0.0

        return Grader.normalize_score(score)  # ✅ FIX