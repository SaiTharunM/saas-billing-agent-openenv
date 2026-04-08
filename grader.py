import math
from typing import Any, Callable, Dict

from engine import SaaSSupportEnv
from models import ActionType, TicketStatus


def clamp_score(score: float) -> float:
    """Return a score strictly inside the validator-safe interval."""
    return float(max(0.01, min(0.99, float(score))))


class Grader:
    @staticmethod
    def normalize(score: Any) -> float:
        try:
            value = float(score)
        except (TypeError, ValueError):
            return 0.5

        if value is None or math.isnan(value):
            return 0.5

        return clamp_score(value)

    @staticmethod
    def grade_task_1(env: SaaSSupportEnv) -> float:
        current_ticket = getattr(env, "current_ticket", None) or {}
        history = current_ticket.get("history", []) if isinstance(current_ticket, dict) else []
        customer_email = (
            getattr(getattr(env, "db", None), "customers", {})
            .get("cust_001", {})
            .get("email")
        )

        verified = getattr(env, "verification_pending", False) or any(
            "Security: Please verify" in getattr(msg, "content", "")
            for msg in history
        )
        updated = customer_email == "alice_new@example.com"
        resolved = current_ticket.get("status") == TicketStatus.RESOLVED

        if updated and resolved:
            return clamp_score(0.99)
        if verified:
            return clamp_score(0.5)
        return clamp_score(0.01)

    @staticmethod
    def grade_task_2(env: SaaSSupportEnv) -> float:
        history = getattr(env, "action_history", []) or []
        looked_up = any(a.action_type == ActionType.LOOKUP_BILLING for a in history)

        correct_refund = False
        any_refund = False

        for action in history:
            if action.action_type == ActionType.TRIGGER_REFUND:
                any_refund = True
                payload = action.payload or {}

                try:
                    amount = float(payload.get("amount", 0))
                except (TypeError, ValueError):
                    amount = 0.0

                if (
                    payload.get("invoice_id") == "inv_101"
                    and abs(amount - 14.99) < 0.01
                ):
                    correct_refund = True

        if correct_refund:
            return clamp_score(0.99)
        if any_refund:
            return clamp_score(0.5)
        if looked_up:
            return clamp_score(0.2)
        return clamp_score(0.01)

    @staticmethod
    def grade_task_3(env: SaaSSupportEnv) -> float:
        history = getattr(env, "action_history", []) or []

        loyalty_offered = any(
            a.action_type == ActionType.OFFER_LOYALTY_DISCOUNT for a in history
        )
        refund_issued = any(
            a.action_type == ActionType.TRIGGER_REFUND for a in history
        )

        if loyalty_offered and not refund_issued:
            return clamp_score(0.99)
        if loyalty_offered and refund_issued:
            return clamp_score(0.5)
        return clamp_score(0.01)

    @staticmethod
    def grade(task_id: str, env: SaaSSupportEnv) -> float:
        if env is None:
            env = SaaSSupportEnv()

        current_ticket = getattr(env, "current_ticket", None)
        if not current_ticket:
            try:
                env.reset(task_id=task_id)
            except Exception:
                return clamp_score(0.01)

        grader = TASK_GRADERS.get(task_id)
        if grader is None:
            return clamp_score(0.01)

        try:
            return float(clamp_score(float(grader(env))))
        except Exception:
            return clamp_score(0.01)


TASK_GRADERS: Dict[str, Callable[[SaaSSupportEnv], float]] = {
    "task_1": Grader.grade_task_1,
    "task_2": Grader.grade_task_2,
    "task_3": Grader.grade_task_3,
}
