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

    raise KeyError(f"Unknown task_id: {task_id}")


def main() -> None:
    for task_id in TASK_IDS:
        env = SaaSSupportEnv()
        env.reset(task_id=task_id)
        solve_task(env, task_id)
        raw_score = TASK_GRADERS[task_id](env)
        clamped_score = Grader.grade(task_id, env)
        print(
            f"task={task_id} raw_score={raw_score:.4f} clamped_score={clamped_score:.4f} steps={env.steps_taken}"
        )


if __name__ == "__main__":
    main()
