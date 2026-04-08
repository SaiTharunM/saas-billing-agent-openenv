import unittest

from engine import SaaSSupportEnv
from grader import Grader, TASK_GRADERS
from models import Action, ActionType
from tasks import TASK_IDS


def solve_task(env: SaaSSupportEnv, task_id: str) -> None:
    if task_id == "task_1":
        env.step(
            Action(
                action_type=ActionType.UPDATE_CUSTOMER_RECORD,
                payload={"field": "email", "value": "alice_new@example.com"},
            )
        )
        env.step(
            Action(
                action_type=ActionType.UPDATE_CUSTOMER_RECORD,
                payload={"field": "email", "value": "alice_new@example.com"},
            )
        )
        env.step(Action(action_type=ActionType.CLOSE_TICKET, payload={}))
        return

    if task_id == "task_2":
        env.step(Action(action_type=ActionType.LOOKUP_BILLING, payload={}))
        env.step(
            Action(
                action_type=ActionType.TRIGGER_REFUND,
                payload={"invoice_id": "inv_101", "amount": 14.99},
            )
        )
        return

    if task_id == "task_3":
        env.step(Action(action_type=ActionType.OFFER_LOYALTY_DISCOUNT, payload={}))
        return

    raise AssertionError(f"Unhandled task in test solver: {task_id}")


class GraderValidationTests(unittest.TestCase):
    def test_all_registered_tasks_have_graders(self) -> None:
        self.assertGreaterEqual(len(TASK_IDS), 3)
        self.assertTrue(set(TASK_IDS).issubset(TASK_GRADERS.keys()))

    def test_graders_return_strictly_bounded_scores(self) -> None:
        for task_id in TASK_IDS:
            env = SaaSSupportEnv()
            env.reset(task_id=task_id)
            solve_task(env, task_id)
            score = Grader.grade(task_id, env)

            self.assertIsInstance(score, float)
            self.assertGreater(score, 0.0)
            self.assertLess(score, 1.0)


if __name__ == "__main__":
    unittest.main()
