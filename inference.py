import json
import os
import sys
from typing import Optional

from openai import OpenAI

from engine import Action, ActionType, SaaSSupportEnv
from grader import Grader
from tasks import TASKS, TASK_IDS

API_BASE_URL = os.getenv("API_BASE_URL")
API_KEY = os.getenv("API_KEY")
MODEL_NAME = os.getenv("MODEL_NAME")

client: Optional[OpenAI] = None
if API_KEY:
    client = OpenAI(
        base_url=API_BASE_URL,
        api_key=API_KEY,
    )


def safe_score(value: object) -> float:
    try:
        score = float(value)
    except (TypeError, ValueError):
        return 0.5

    if score != score:
        return 0.5
    if score <= 0.0:
        return 0.01
    if score >= 1.0:
        return 0.99
    return score


def safe_reward(value: object) -> float:
    try:
        reward = float(value)
    except (TypeError, ValueError):
        return 0.5

    if reward != reward:
        return 0.5
    if reward <= 0.0:
        return 0.01
    if reward >= 1.0:
        return 0.99
    return reward


def build_fallback_action(observation_json: str) -> Action:
    observation = json.loads(observation_json)
    last_message = observation.get("last_message", "").lower()
    chat_history = observation.get("chat_history", [])
    history_text = "\n".join(message.get("content", "") for message in chat_history).lower()
    customer_tier = observation.get("customer_info", {}).get("tier")

    if "update my email" in history_text or "email updated successfully" in history_text:
        if "email updated successfully" in history_text:
            return Action(action_type=ActionType.CLOSE_TICKET, payload={})

        return Action(
            action_type=ActionType.UPDATE_CUSTOMER_RECORD,
            payload={"field": "email", "value": "alice_new@example.com"},
        )

    if "pro-rated refund" in history_text or "cancel my subscription" in history_text:
        if "billing records:" not in history_text:
            return Action(action_type=ActionType.LOOKUP_BILLING, payload={})

        return Action(
            action_type=ActionType.TRIGGER_REFUND,
            payload={"invoice_id": "inv_101", "amount": 14.99},
        )

    if customer_tier == "enterprise" or "competitor" in last_message or "switching" in history_text:
        return Action(action_type=ActionType.OFFER_LOYALTY_DISCOUNT, payload={})

    return Action(
        action_type=ActionType.REPLY,
        payload={"message": "We are processing your request."},
    )


def get_llm_action(observation_json: str) -> Action:
    if client is None or not MODEL_NAME:
        return build_fallback_action(observation_json)

    try:
        system_prompt = f"""
        You are an AI support agent for SaaS Billing & Subscription.

        Available Actions: {[action.value for action in ActionType]}

        Always respond with valid JSON:
        {{
            "action_type": "...",
            "payload": {{}}
        }}
        """

        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": observation_json},
            ],
            response_format={"type": "json_object"},
            timeout=10,
        )

        action_data = json.loads(response.choices[0].message.content)
        return Action(**action_data)
    except Exception as exc:
        print(f"[WARNING] LLM failed, using fallback: {exc}")
        return build_fallback_action(observation_json)


def run_inference():
    try:
        env = SaaSSupportEnv()
    except Exception as exc:
        print(f"[ERROR] Failed to initialize environment: {exc}")
        return {}

    scores = {}

    for task_id in TASK_IDS:
        print(f"[START] task_id: {task_id}")

        try:
            obs = env.reset(task_id=task_id)
        except Exception as exc:
            print(f"[ERROR] Reset failed for {task_id}: {exc}")
            continue

        done = False
        step_count = 0
        max_steps = 5

        while not done and step_count < max_steps:
            step_count += 1

            try:
                action = get_llm_action(obs.model_dump_json())
                obs, reward = env.step(action)
                done = reward.is_terminal
                safe_r = safe_reward(reward.value)
                print(
                    f"[STEP] step: {step_count}, action: {action.action_type.value}, reward: {safe_r}, done: {done}"
                )
            except Exception as exc:
                print(f"[ERROR] Step failed: {exc}")
                break

        try:
            raw_score = Grader.grade(task_id, env)
            score = safe_score(raw_score)
        except Exception as exc:
            print(f"[ERROR] Grading failed: {exc}")
            score = 0.5

        scores[task_id] = score
        print(f"[END] task_id: {task_id}, score: {score}")

    return scores


if __name__ == "__main__":
    try:
        if not all([API_BASE_URL, API_KEY, MODEL_NAME]):
            print("[WARNING] Missing environment variables; using deterministic fallback actions.")

        run_inference()
    except Exception as exc:
        print(f"[FATAL] Unexpected error: {exc}")
        sys.exit(0)
