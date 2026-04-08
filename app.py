import os
import time
from contextlib import asynccontextmanager

import uvicorn
from openai import OpenAI
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import ValidationError, BaseModel
from engine import SaaSSupportEnv
from models import Action
from tasks import TASKS, list_tasks
from grader import Grader

API_BASE_URL = os.getenv("API_BASE_URL")
API_KEY = os.getenv("API_KEY") or os.getenv("HF_TOKEN") or os.getenv("OPENAI_API_KEY")
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4o-mini")


def ping_llm_proxy() -> None:
    if not API_BASE_URL or not API_KEY:
        return

    try:
        client = OpenAI(base_url=API_BASE_URL, api_key=API_KEY)
        client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": "Return terse JSON only."},
                {"role": "user", "content": '{"status":"startup"}'},
            ],
            response_format={"type": "json_object"},
            max_tokens=16,
            timeout=10,
        )
    except Exception:
        return


@asynccontextmanager
async def lifespan(_: FastAPI):
    ping_llm_proxy()
    yield


app = FastAPI(title="SaaS Billing Support OpenEnv API", lifespan=lifespan)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

env = SaaSSupportEnv()
current_task_id = None
start_time = time.time()

class ResetRequest(BaseModel):
    """Request model for resetting the environment."""
    task_id: str = "task_1"

@app.exception_handler(ValidationError)
async def validation_exception_handler(request: Request, exc: ValidationError):
    """Handles Pydantic validation errors."""
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors(), "body": str(exc)},
    )

@app.middleware("http")
async def catch_exceptions_middleware(request: Request, call_next):
    """Global exception handler for internal server errors."""
    try:
        return await call_next(request)
    except Exception as exc:
        import traceback
        print(f"500 Internal Server Error: {exc}")
        traceback.print_exc()
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal Server Error", "message": str(exc)},
        )

@app.get("/health")
async def health():
    """Returns the health status of the API."""
    return {"status": "ok"}

@app.get("/", response_class=HTMLResponse)
async def root():
    """Serves the professional enterprise dashboard."""
    uptime = int(time.time() - start_time)
    task_count = len(TASKS)
    active_task = current_task_id or "None (Call /reset)"
    
    return f"""
    <!DOCTYPE html>
    <html lang="en" class="scroll-smooth">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>SaaS Billing OpenEnv | Enterprise Dashboard</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
        <style>
            body {{ font-family: 'Inter', sans-serif; }}
            .mono {{ font-family: 'JetBrains Mono', monospace; }}
            @keyframes fadeIn {{
                from {{ opacity: 0; transform: translateY(10px); }}
                to {{ opacity: 1; transform: translateY(0); }}
            }}
            .fade-in {{ animation: fadeIn 0.6s ease-out forwards; }}
            .pulse-green {{
                box-shadow: 0 0 0 0 rgba(34, 197, 94, 0.7);
                animation: pulse-green 2s infinite;
            }}
            @keyframes pulse-green {{
                0% {{ transform: scale(0.95); box-shadow: 0 0 0 0 rgba(34, 197, 94, 0.7); }}
                70% {{ transform: scale(1); box-shadow: 0 0 0 10px rgba(34, 197, 94, 0); }}
                100% {{ transform: scale(0.95); box-shadow: 0 0 0 0 rgba(34, 197, 94, 0); }}
            }}
        </style>
    </head>
    <body class="bg-[#0a0a0c] text-slate-300 min-h-screen selection:bg-blue-500/30">
        <div class="fade-in opacity-0">
            <!-- Navigation -->
            <nav class="border-b border-white/5 bg-black/20 backdrop-blur-xl sticky top-0 z-50">
                <div class="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
                    <div class="flex items-center gap-3">
                        <div class="w-9 h-9 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-xl flex items-center justify-center shadow-lg shadow-blue-500/20">
                            <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M13 10V3L4 14h7v7l9-11h-7z"></path></svg>
                        </div>
                        <span class="text-lg font-bold tracking-tight text-white">SaaS Billing <span class="text-blue-500">OpenEnv</span></span>
                    </div>
                    <div class="flex items-center gap-6">
                        <span class="text-xs font-medium text-slate-500 uppercase tracking-widest">v2.1.0 Enterprise</span>
                        <div class="h-4 w-px bg-white/10"></div>
                        <a href="https://huggingface.co/spaces" class="text-sm font-medium hover:text-white transition">HF Space</a>
                    </div>
                </div>
            </nav>

            <main class="max-w-7xl mx-auto px-6 py-12">
                <div class="grid grid-cols-1 lg:grid-cols-12 gap-8">
                    
                    <!-- Left Side: Status & Controls -->
                    <div class="lg:col-span-5 space-y-6">
                        <div class="bg-[#111114] border border-white/5 rounded-3xl p-8 shadow-2xl">
                            <div class="flex items-center justify-between mb-8">
                                <div class="flex items-center gap-3">
                                    <div class="w-3 h-3 rounded-full bg-green-500 pulse-green"></div>
                                    <span class="text-xs font-bold text-green-500 uppercase tracking-widest">System Online</span>
                                </div>
                                <span class="text-[10px] mono text-slate-600">ID: ENV-SB-7860</span>
                            </div>

                            <h1 class="text-3xl font-bold text-white mb-4 leading-tight">Environment Control Center</h1>
                            <p class="text-slate-400 text-sm leading-relaxed mb-8">
                                Real-time monitoring and control interface for the SaaS Billing Support OpenEnv. 
                                Designed for high-fidelity agent training and policy evaluation.
                            </p>

                            <div class="grid grid-cols-2 gap-4 mb-8">
                                <div class="bg-white/5 border border-white/5 p-5 rounded-2xl">
                                    <div class="text-slate-500 text-[10px] font-bold uppercase tracking-widest mb-1">Uptime</div>
                                    <div class="text-xl font-semibold text-white mono">{uptime}s</div>
                                </div>
                                <div class="bg-white/5 border border-white/5 p-5 rounded-2xl">
                                    <div class="text-slate-500 text-[10px] font-bold uppercase tracking-widest mb-1">Active Task</div>
                                    <div class="text-xl font-semibold text-blue-400 mono truncate">{active_task}</div>
                                </div>
                                <div class="bg-white/5 border border-white/5 p-5 rounded-2xl">
                                    <div class="text-slate-500 text-[10px] font-bold uppercase tracking-widest mb-1">API Port</div>
                                    <div class="text-xl font-semibold text-white mono">7860</div>
                                </div>
                                <div class="bg-white/5 border border-white/5 p-5 rounded-2xl">
                                    <div class="text-slate-500 text-[10px] font-bold uppercase tracking-widest mb-1">Task Count</div>
                                    <div class="text-xl font-semibold text-white mono">{task_count}</div>
                                </div>
                            </div>

                            <div class="space-y-3">
                                <a href="/docs" class="flex items-center justify-between w-full bg-blue-600 hover:bg-blue-500 text-white px-6 py-4 rounded-2xl font-semibold transition-all group">
                                    <span class="flex items-center gap-3">
                                        <span>📜</span> API Documentation
                                    </span>
                                    <svg class="w-5 h-5 group-hover:translate-x-1 transition" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 8l4 4m0 0l-4 4m4-4H3"></path></svg>
                                </a>
                                <div class="grid grid-cols-2 gap-3">
                                    <a href="/tasks" class="flex items-center justify-center gap-2 bg-white/5 hover:bg-white/10 border border-white/5 text-white px-4 py-4 rounded-2xl font-medium transition">
                                        <span>🛠️</span> Tasks
                                    </a>
                                    <a href="/state" class="flex items-center justify-center gap-2 bg-white/5 hover:bg-white/10 border border-white/5 text-white px-4 py-4 rounded-2xl font-medium transition">
                                        <span>📊</span> State
                                    </a>
                                </div>
                            </div>
                        </div>

                        <div class="bg-blue-500/5 border border-blue-500/10 rounded-3xl p-6">
                            <div class="flex gap-4">
                                <div class="w-10 h-10 bg-blue-500/20 rounded-xl flex items-center justify-center shrink-0">
                                    <svg class="w-5 h-5 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
                                </div>
                                <div>
                                    <h4 class="text-blue-400 font-bold text-sm mb-1">Pro-Rated Logic Enabled</h4>
                                    <p class="text-xs text-blue-300/60 leading-relaxed">
                                        The environment now supports deterministic pro-rated refund calculations. Ensure agents use the <code class="mono text-blue-300">lookup_billing</code> tool to fetch cycle dates.
                                    </p>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Right Side: Schema Documentation -->
                    <div class="lg:col-span-7">
                        <div class="bg-[#111114] border border-white/5 rounded-3xl overflow-hidden shadow-2xl h-full flex flex-col">
                            <div class="p-6 border-b border-white/5 bg-white/[0.02] flex items-center justify-between">
                                <h2 class="text-sm font-bold uppercase tracking-widest text-white">Schema Reference</h2>
                                <div class="flex gap-2">
                                    <div class="w-2 h-2 rounded-full bg-slate-800"></div>
                                    <div class="w-2 h-2 rounded-full bg-slate-800"></div>
                                    <div class="w-2 h-2 rounded-full bg-slate-800"></div>
                                </div>
                            </div>
                            
                            <div class="p-0 flex-grow overflow-auto">
                                <table class="w-full text-left border-collapse">
                                    <thead>
                                        <tr class="bg-white/[0.01]">
                                            <th class="px-6 py-4 text-[10px] font-bold text-slate-500 uppercase tracking-widest border-b border-white/5">Action Type</th>
                                            <th class="px-6 py-4 text-[10px] font-bold text-slate-500 uppercase tracking-widest border-b border-white/5">Payload Fields</th>
                                            <th class="px-6 py-4 text-[10px] font-bold text-slate-500 uppercase tracking-widest border-b border-white/5">Constraint</th>
                                        </tr>
                                    </thead>
                                    <tbody class="text-xs mono">
                                        <tr class="hover:bg-white/[0.02] transition">
                                            <td class="px-6 py-4 text-blue-400 font-medium border-b border-white/5">reply</td>
                                            <td class="px-6 py-4 text-slate-400 border-b border-white/5">message: string</td>
                                            <td class="px-6 py-4 text-slate-500 border-b border-white/5">Stochastic Response</td>
                                        </tr>
                                        <tr class="hover:bg-white/[0.02] transition">
                                            <td class="px-6 py-4 text-blue-400 font-medium border-b border-white/5">lookup_billing</td>
                                            <td class="px-6 py-4 text-slate-400 border-b border-white/5">{{}}</td>
                                            <td class="px-6 py-4 text-slate-500 border-b border-white/5">Reward: +0.1</td>
                                        </tr>
                                        <tr class="hover:bg-white/[0.02] transition">
                                            <td class="px-6 py-4 text-blue-400 font-medium border-b border-white/5">trigger_refund</td>
                                            <td class="px-6 py-4 text-slate-400 border-b border-white/5">invoice_id, amount</td>
                                            <td class="px-6 py-4 text-slate-500 border-b border-white/5">30-day Window</td>
                                        </tr>
                                        <tr class="hover:bg-white/[0.02] transition">
                                            <td class="px-6 py-4 text-blue-400 font-medium border-b border-white/5">update_record</td>
                                            <td class="px-6 py-4 text-slate-400 border-b border-white/5">field, value</td>
                                            <td class="px-6 py-4 text-slate-500 border-b border-white/5">Verification Required</td>
                                        </tr>
                                        <tr class="hover:bg-white/[0.02] transition">
                                            <td class="px-6 py-4 text-blue-400 font-medium border-b border-white/5">loyalty_discount</td>
                                            <td class="px-6 py-4 text-slate-400 border-b border-white/5">{{}}</td>
                                            <td class="px-6 py-4 text-slate-500 border-b border-white/5">Enterprise Only</td>
                                        </tr>
                                    </tbody>
                                </table>

                                <div class="p-8 space-y-6">
                                    <div>
                                        <h3 class="text-[10px] font-bold text-slate-500 uppercase tracking-widest mb-4">Observation Schema</h3>
                                        <div class="bg-black/40 rounded-2xl p-6 border border-white/5 mono text-[11px] leading-relaxed">
                                            <span class="text-purple-400">"observation"</span>: {{<br>
                                            &nbsp;&nbsp;<span class="text-blue-400">"ticket_id"</span>: <span class="text-green-400">"string"</span>,<br>
                                            &nbsp;&nbsp;<span class="text-blue-400">"customer_info"</span>: {{ <span class="text-slate-500">"tier": "enterprise", ...</span> }},<br>
                                            &nbsp;&nbsp;<span class="text-blue-400">"chat_history"</span>: [ <span class="text-slate-500">{{ "role": "agent", "content": "..." }}</span> ],<br>
                                            &nbsp;&nbsp;<span class="text-blue-400">"available_tools"</span>: [ <span class="text-green-400">"reply", "refund", ...</span> ]<br>
                                            }}
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </main>

            <footer class="max-w-7xl mx-auto px-6 py-12 border-t border-white/5 flex flex-col sm:flex-row justify-between items-center gap-4">
                <div class="text-slate-500 text-xs tracking-wide">
                    &copy; 2024 SaaS Billing Support OpenEnv &bull; Competition Entry
                </div>
                <div class="flex gap-6">
                    <a href="#" class="text-slate-500 hover:text-white transition text-xs font-medium">Terms</a>
                    <a href="#" class="text-slate-500 hover:text-white transition text-xs font-medium">Privacy</a>
                    <a href="#" class="text-slate-500 hover:text-white transition text-xs font-medium">Security</a>
                </div>
            </footer>
        </div>
    </body>
    </html>
    """

@app.post("/reset")
async def reset(request: Request, task_id: str = None):
    """
    Resets the environment for a specific task.
    Accepts task_id from query params or JSON body.
    """
    global current_task_id
    
    # Try to get task_id from body if not in query params
    if task_id is None:
        try:
            body = await request.json()
            task_id = body.get("task_id")
        except:
            pass
    
    # Default to task_1
    if task_id is None:
        task_id = "task_1"
        
    if task_id not in TASKS:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    
    current_task_id = task_id
    obs = env.reset(task_id=task_id)
    return obs

@app.post("/step")
async def step(action: Action):
    """Executes an agent action and returns the observation and reward."""
    if current_task_id is None:
        raise HTTPException(status_code=400, detail="Environment not reset. Call /reset first.")
    
    obs, reward = env.step(action)
    return {
        "observation": obs,
        "reward": reward.value,
        "done": reward.is_terminal,
        "info": {"reason": reward.reason}
    }

@app.get("/state")
async def get_state():
    """Returns the full internal state of the environment."""
    return env.state()

@app.get("/tasks")
async def get_tasks():
    """Returns the list of available tasks as a JSON list."""
    return list_tasks()

@app.get("/grader")
async def get_grader():
    """Returns the score for the current task."""
    if current_task_id is None:
        raise HTTPException(status_code=400, detail="No active task. Call /reset first.")
    
    score = Grader.grade(current_task_id, env)
        
    return {
        "task_id": current_task_id, 
        "score": score,
        "is_terminal": env.is_terminal
    }

if __name__ == "__main__":
    # Hard-coded port 7860 for Hugging Face Spaces
    port = int(os.environ.get("PORT", 7860))
    uvicorn.run(app, host="0.0.0.0", port=port)
