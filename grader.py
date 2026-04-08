import math
from typing import Any, Callable, Dict
from engine import SaaSSupportEnv
from models import ActionType, TicketStatus

class Grader:

    @staticmethod
    def normalize(score: Any) -> float:
        try:
            s = float(score)
        except (TypeError, ValueError):
            return 0.5

        if s is None or math.isnan(s):
            return 0.5

        if s <= 0.0:
            return 0.01
        if s >= 1.0:
            return 0.99

        return s

    @staticmethod
    def grade_task_1(env: SaaSSupportEnv) -> float:
        verified = env.verification_pending or any(
            "Security: Please verify" in msg.content
            for msg in env.current_ticket["history"]
        )

        updated = env.db.customers["cust_001"]["email"] == "alice_new@example.com"
        resolved = env.current_ticket["status"] == TicketStatus.RESOLVED

        if updated and resolved:
            return Grader.normalize(0.99)   # ❌ NOT 1.0
        if verified:
            return Grader.normalize(0.5)
        return Grader.normalize(0.01)       # ❌ NOT 0.0

    @staticmethod
    def grade_task_2(env: SaaSSupportEnv) -> float:
        history = env.action_history

        looked_up = any(a.action_type == ActionType.LOOKUP_BILLING for a in history)

        correct_refund = False
        any_refund = False

        for action in history:
            if action.action_type == ActionType.TRIGGER_REFUND:
                any_refund = True
                payload = action.payload or {}

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
            return Grader.normalize(0.99)
        if any_refund:
            return Grader.normalize(0.5)
        if looked_up:
            return Grader.normalize(0.2)

        return Grader.normalize(0.01)

    @staticmethod
    def grade_task_3(env: SaaSSupportEnv) -> float:
        history = env.action_history

        loyalty_offered = any(
            a.action_type == ActionType.OFFER_LOYALTY_DISCOUNT for a in history
        )

        refund_issued = any(
            a.action_type == ActionType.TRIGGER_REFUND for a in history
        )

        if loyalty_offered and not refund_issued:
            return Grader.normalize(0.99)
        if loyalty_offered and refund_issued:
            return Grader.normalize(0.5)

        return Grader.normalize(0.01)

    @staticmethod
    def grade(task_id: str, env: SaaSSupportEnv) -> float:
        grader = TASK_GRADERS.get(task_id)
        if grader is None:
            return Grader.normalize(0.01)
        return Grader.normalize(grader(env))


TASK_GRADERS: Dict[str, Callable[[SaaSSupportEnv], float]] = {
    "task_1": Grader.grade_task_1,
    "task_2": Grader.grade_task_2,
    "task_3": Grader.grade_task_3,
}
