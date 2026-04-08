---
title: SaaS Billing Support Agent
emoji: "💰"
colorFrom: blue
colorTo: indigo
sdk: docker
app_file: app.py
pinned: false
---

# SaaS Billing Support OpenEnv

A stateful OpenEnv environment for SaaS billing and subscription support workflows. The environment exposes typed observations, deterministic task graders, bounded rewards, and a reproducible inference runner.

## Features

- FastAPI environment with `reset()`, `step()`, `state()`, `/tasks`, and `/grader`
- Three registered tasks covering easy, medium, and hard billing support flows
- Deterministic graders with scores strictly inside `(0, 1)`
- Inference script at the repo root named `inference.py`
- Docker deployment for Hugging Face Spaces

## Action Space

| Action Type | Payload Fields | Description |
| :--- | :--- | :--- |
| `reply` | `message` | Send a response to the customer |
| `lookup_billing` | none | Fetch billing history for the active customer |
| `trigger_refund` | `invoice_id`, `amount` | Issue a refund for a valid invoice |
| `update_customer_record` | `field`, `value` | Update customer metadata after verification |
| `offer_loyalty_discount` | none | Offer a retention discount for enterprise customers |
| `close_ticket` | none | Resolve the active ticket |

## Observation Space

| Field | Type | Description |
| :--- | :--- | :--- |
| `ticket_id` | `string` | Active ticket identifier |
| `customer_info` | `object` | Customer name and tier |
| `last_message` | `string` | Latest customer-facing message |
| `chat_history` | `array` | Full transcript for the task |
| `available_tools` | `array` | Allowed action types |
| `current_status` | `string` | Ticket status |

## Tasks

| Task ID | Difficulty | Objective | Score Range |
| :--- | :--- | :--- | :--- |
| `task_1` | easy | Update a customer email after verification | `(0.01, 0.99)` |
| `task_2` | medium | Calculate and issue a pro-rated refund | `(0.01, 0.99)` |
| `task_3` | hard | Retain an enterprise customer with a loyalty offer | `(0.01, 0.99)` |

## Reward Design

- Exposed rewards are normalized into `(0, 1)` before being returned by the environment
- Successful end states cap at `0.99`
- Failed or negative intermediate rewards clamp to `0.01`
- Partial progress is reflected through intermediate values such as billing lookup and partial grader credit

## Local Setup

```bash
pip install -r requirements.txt
python app.py
```

The app listens on `http://localhost:7860`.

## Baseline and Inference

Run the baseline:

```bash
python baseline.py
```

Run the submission inference script:

```bash
python inference.py
```

The inference script prints structured stdout logs in the required format:

- `[START]`
- `[STEP]`
- `[END]`

## Docker

```bash
docker build -t saas-billing-env .
docker run -p 7860:7860 saas-billing-env
```

## Validation Notes

- `openenv.yaml` declares a reward range of `[0.01, 0.99]`
- All graders return floats strictly inside `(0, 1)`
- The environment registers all three tasks consistently across config, runtime, and inference
