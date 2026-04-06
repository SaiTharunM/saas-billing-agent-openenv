import os
import json
import sys
from openai import OpenAI
from engine import SaaSSupportEnv, Action, ActionType
from tasks import TASKS
from grader import Grader

# Mandatory environment variables
API_BASE_URL = os.getenv("API_BASE_URL")
MODEL_NAME = os.getenv("MODEL_NAME")
HF_TOKEN = os.getenv("HF_TOKEN")

# Initialize OpenAI client
# Note: We use HF_TOKEN as the api_key for the OpenAI client when calling HF endpoints or similar
client = OpenAI(
    base_url=API_BASE_URL,
    api_key=HF_TOKEN
)

def get_llm_action(observation_json: str) -> Action:
    """
    Calls the LLM to decide the next action based on the observation.
    """
    system_prompt = f"""
    You are an AI support agent for a SaaS Billing & Subscription environment.
    Your goal is to resolve the customer's issue efficiently and correctly.
    
    Available Action Types: {[a.value for a in ActionType]}
    
    Action Schema:
    - action_type: One of the types above.
    - payload: A dictionary of parameters.
      - For 'reply': {{"message": "your response"}}
      - For 'trigger_refund': {{"invoice_id": "inv_XXX"}}
      - For 'update_customer_record': {{"field": "email", "value": "new@email.com"}}
      - For 'update_subscription': {{"tier": "pro"}}
      - For 'lookup_billing', 'close_ticket', 'offer_retention_credit': {{}}
    
    Respond ONLY with a valid JSON object matching the Action schema.
    """
    
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Current Observation: {observation_json}"}
        ],
        response_format={"type": "json_object"}
    )
    
    action_data = json.loads(response.choices[0].message.content)
    return Action(**action_data)

def run_inference():
    env = SaaSSupportEnv()
    
    # Iterate through all tasks defined in tasks.py
    for task_id, task_meta in TASKS.items():
        print(f"[START] task_id: {task_id}")
        
        obs = env.reset(
            ticket_id=task_meta["id"],
            customer_id=task_meta["customer_id"],
            initial_message=task_meta["initial_message"]
        )
        
        done = False
        step_count = 0
        max_steps = 5 # Prevent infinite loops
        
        while not done and step_count < max_steps:
            step_count += 1
            
            # 1. Get action from LLM
            try:
                action = get_llm_action(obs.model_dump_json())
            except Exception as e:
                # In case of LLM failure, we log and break the task
                print(f"Error getting action for {task_id} at step {step_count}: {e}")
                break
                
            # 2. Step the environment
            obs, reward = env.step(action)
            done = reward.is_terminal
            
            # Mandatory structured log format
            print(f"[STEP] step: {step_count}, action: {action.action_type.value}, reward: {reward.value}, done: {done}")
        
        # 3. Grade the final state using the task-specific grader
        if task_id == "task_1":
            score = Grader.grade_task_1(env)
        elif task_id == "task_2":
            score = Grader.grade_task_2(env)
        elif task_id == "task_3":
            score = Grader.grade_task_3(env)
        else:
            score = 0.0
            
        # Mandatory structured log format
        print(f"[END] task_id: {task_id}, score: {score}")

if __name__ == "__main__":
    # Validate environment variables
    if not all([API_BASE_URL, MODEL_NAME, HF_TOKEN]):
        print("Error: Mandatory environment variables (API_BASE_URL, MODEL_NAME, HF_TOKEN) not set.")
        # We don't exit with 1 here to allow the script to be "runnable" even if it fails immediately, 
        # but in a real submission environment these will be present.
        sys.exit(1)
        
    run_inference()
