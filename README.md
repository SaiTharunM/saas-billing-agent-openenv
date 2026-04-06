# 🚀 SaaS Billing Support OpenEnv

[![OpenEnv Certified](https://img.shields.io/badge/OpenEnv-Certified-blueviolet?style=for-the-badge&logo=openai)](https://openenv.org)
[![Hugging Face Space](https://img.shields.io/badge/%F0%9F%A4%97%20Hugging%20Face-Space-yellow?style=for-the-badge)](https://huggingface.co/spaces)

> **The ultimate high-fidelity simulator for training AI agents in complex SaaS billing operations, policy reasoning, and pro-rated mathematics.**

---

## 🎯 The Mission

In the modern enterprise, billing isn't just about invoices; it's about **policy-governed reasoning**. Agents must navigate pro-rated refund windows, verify customer identities, and balance retention goals against strict financial controls. Most simulators fail to capture the "messy middle"—the stochastic customer who is frustrated, the vague request that requires a database lookup, or the policy that forbids a refund but encourages a loyalty discount.

**SaaS Billing Support OpenEnv** provides a robust, stateful environment where agents are tested on their ability to think like a professional support representative. It moves beyond simple text generation into **verifiable action sequences** that update a simulated production database.

---

## 🛠️ Action Space

The agent interacts with the environment using a typed action schema. Every action (except `reply`) requires specific parameters and is validated against the `CompanyPolicy`.

| Action Type | Payload Fields | Description |
| :--- | :--- | :--- |
| `reply` | `message: string` | Send a text response to the customer. |
| `lookup_billing` | `{}` | Retrieve the customer's full billing history and usage logs. |
| `trigger_refund` | `invoice_id, amount` | Issue a refund. Validated against the 30-day policy window. |
| `update_record` | `field, value` | Update customer metadata (e.g., email). Requires verification. |
| `loyalty_discount` | `{}` | Offer a 15% discount to Enterprise customers for retention. |

---

## 👁️ Observation Space

The environment returns a comprehensive state object after every step, allowing for sophisticated chain-of-thought reasoning.

| Field | Type | Description |
| :--- | :--- | :--- |
| `ticket_id` | `string` | Unique identifier for the current support session. |
| `customer_info` | `object` | Metadata including `tier`, `join_date`, and `is_verified`. |
| `chat_history` | `list` | Full transcript of the conversation so far. |
| `available_tools`| `list` | List of actions currently permitted by the system. |

---


## 📊 Difficulty Matrix & Tasks

We provide three distinct tasks that test different dimensions of agent capability.

| Task ID | Difficulty | Objective | Grading Logic (0.0 - 1.0) |
| :--- | :--- | :--- | :--- |
| `task_1` | **Easy** | Update customer email. | Correct field update + Verification + Resolution. |
| `task_2` | **Medium** | Calculate pro-rated refund. | Billing lookup + Correct math + Policy adherence. |
| `task_3` | **Hard** | Retention vs. Refund. | Identify Enterprise tier + Offer Loyalty + No Refund. |

---

## 📈 Reward Shaping

Our reward function provides dense signals to guide the agent toward optimal behavior:

- **Success Bonus:** `+1.0` for perfect task completion.
- **Information Gain:** `+0.1` for performing a `lookup_billing` (encourages data-driven decisions).
- **Policy Penalty:** `-0.5` for attempting an illegal refund (e.g., outside 30-day window).
- **Hallucination Penalty:** `-0.2` for issuing a refund without looking up the invoice first.
- **Time Penalty:** `-0.01` per step to encourage efficiency.

---
## 📊 Tasks & Evaluation

| Task | Objective | Result |
|------|----------|--------|
| task_1 | Email Update + Verification | ✅ 1.0 |
| task_2 | Pro-rated Refund | ✅ 1.0 |
| task_3 | Retention Strategy | ✅ 1.0 |

---

## 📈 Reward System

- ✅ +1.0 → Perfect completion  
- ➕ +0.1 → Data lookup  
- ❌ -0.5 → Policy violation  
- ❌ -0.2 → Incorrect reasoning  
- ⏱ -0.01 → Per step penalty  

---

## 🏁 Quick Start (Reproducibility)

To reproduce our baseline scores and verify the environment:

### 💻 Running Locally

This project is a **Full-Stack Application**. Do **not** open `index.html` directly with "Live Server". Instead, run the backend server to see the interactive dashboard.

#### Option 1: Python (Recommended)
```bash
pip install -r requirements.txt
python app.py
```
Visit `http://localhost:7860` in your browser.

#### Option 2: Node.js (Development)
```bash
npm install
npm run dev
```
Visit `http://localhost:3000` in your browser.

### 🐳 Docker Deployment
1. **Clone & Build:**
   ```bash
   docker build -t saas-billing-env .
   docker run -p 7860:7860 saas-billing-env
   ```

2. **Run Baseline:**
   ```bash
   # Ensure APP_URL is set to your local or remote endpoint
   export APP_URL="http://localhost:7860"
   python baseline.py
   ```

3. **Verify Scores:**
   The `baseline.py` script will output a JSON report with scores for all 3 tasks, ensuring the environment is responding deterministically to standard policies.

---

## 📜 License & Compliance
This environment is compliant with the **OpenEnv v2.1.0** specification. All customer data is synthetic and generated for simulation purposes.
