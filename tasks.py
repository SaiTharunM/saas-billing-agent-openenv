from typing import Any, Dict, List

TASKS: Dict[str, Dict[str, Any]] = {
    "task_1": {
        "id": "task_1",
        "task_id": "task_1",
        "ticket_id": "ticket_101",
        "grader": "grade_task_1",
        "name": "Easy: Email Update",
        "description": "Update the customer's email address after verification.",
        "customer_id": "cust_001",
        "initial_message": "I need to update my email to alice_new@example.com. Can you help?",
        "difficulty": "easy",
        "objective": "Update the customer's email address in the database after verification.",
    },
    "task_2": {
        "id": "task_2",
        "task_id": "task_2",
        "ticket_id": "ticket_102",
        "grader": "grade_task_2",
        "name": "Medium: Pro-rated Refund",
        "description": "Calculate and issue a pro-rated refund for a mid-cycle cancellation.",
        "customer_id": "cust_001",
        "initial_message": "I want to cancel my subscription mid-month. Can I get a pro-rated refund for the remaining 15 days?",
        "difficulty": "medium",
        "objective": "Calculate and issue a pro-rated refund (50% of $29.99 = $14.99) for invoice inv_101.",
    },
    "task_3": {
        "id": "task_3",
        "task_id": "task_3",
        "ticket_id": "ticket_103",
        "grader": "grade_task_3",
        "name": "Hard: Retention & Escalation",
        "description": "Retain a high-value Enterprise customer using a loyalty discount.",
        "customer_id": "cust_002",
        "initial_message": "Our company is considering switching to a competitor. What can you offer us to stay?",
        "difficulty": "hard",
        "objective": "Offer a Loyalty Discount to the Enterprise customer instead of a refund to retain them.",
    },
}

TASK_IDS: List[str] = list(TASKS.keys())


def get_task(task_id: str) -> Dict[str, Any]:
    """Returns task metadata for a registered task id."""
    if task_id not in TASKS:
        raise KeyError(f"Unknown task_id: {task_id}")
    return TASKS[task_id]


def list_tasks() -> List[Dict[str, Any]]:
    """Returns task metadata in a stable order."""
    return [TASKS[task_id] for task_id in TASK_IDS]
