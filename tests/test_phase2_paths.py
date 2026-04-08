import unittest

import yaml
from fastapi.testclient import TestClient

import app as app_module
from engine import SaaSSupportEnv
from grader import Grader, TASK_GRADERS
from models import Action, ActionType
from tasks import TASK_IDS, list_tasks


class Phase2PathTests(unittest.TestCase):
    def setUp(self) -> None:
        app_module.current_task_id = None
        app_module.env = SaaSSupportEnv()
        self.client = TestClient(app_module.app)

    def test_openenv_yaml_task_ids_match_registry(self) -> None:
        with open("openenv.yaml", "r", encoding="utf-8") as handle:
            config = yaml.safe_load(handle)

        yaml_task_ids = [task["id"] for task in config["tasks"]]
        yaml_graders = [task["grader"] for task in config["tasks"]]
        registry_task_ids = [task["id"] for task in list_tasks()]
        registry_graders = [task["grader"] for task in list_tasks()]

        self.assertEqual(yaml_task_ids, registry_task_ids)
        self.assertEqual(yaml_graders, registry_graders)
        self.assertEqual(set(TASK_IDS), set(TASK_GRADERS.keys()))

    def test_grader_grade_handles_none_env(self) -> None:
        for task_id in TASK_IDS:
            score = Grader.grade(task_id, None)
            self.assertIsInstance(score, float)
            self.assertGreater(score, 0.0)
            self.assertLess(score, 1.0)

    def test_reward_bounds_hold_for_failure_and_success(self) -> None:
        env = SaaSSupportEnv()
        env.reset(task_id="task_1")
        _, failure_reward = env.step(
            Action(
                action_type=ActionType.UPDATE_CUSTOMER_RECORD,
                payload={"field": "email", "value": "alice_new@example.com"},
            )
        )
        self.assertGreater(failure_reward.value, 0.0)
        self.assertLess(failure_reward.value, 1.0)

        env.reset(task_id="task_1")
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
        _, success_reward = env.step(Action(action_type=ActionType.CLOSE_TICKET, payload={}))
        self.assertGreater(success_reward.value, 0.0)
        self.assertLess(success_reward.value, 1.0)

    def test_api_tasks_and_grader_paths_are_bounded(self) -> None:
        tasks_response = self.client.get("/tasks")
        self.assertEqual(tasks_response.status_code, 200)
        tasks = tasks_response.json()
        self.assertEqual(len(tasks), 3)

        for task in tasks:
            task_id = task["id"]
            grader_response = self.client.get("/grader", params={"task_id": task_id})
            self.assertEqual(grader_response.status_code, 200)
            score = grader_response.json()["score"]
            self.assertGreater(score, 0.0)
            self.assertLess(score, 1.0)


if __name__ == "__main__":
    unittest.main()
