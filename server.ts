import express from 'express';
import { createServer as createViteServer } from 'vite';
import path from 'path';
import { SaaSSupportEnv, Action } from './engine';
import { TASKS } from './tasks';
import { Grader } from './grader';

async function startServer() {
  const app = express();
  const PORT = 3000;

  app.use(express.json());

  const env = new SaaSSupportEnv();
  const startTime = Date.now();
  let currentTaskId: string | null = null;

  app.get('/health', (req, res) => {
    res.json({ status: 'ok' });
  });

  app.get('/', (req, res) => {
    const uptime = Math.floor((Date.now() - startTime) / 1000);
    const taskCount = Object.keys(TASKS).length;
    const activeTask = currentTaskId || "None (Call /reset)";

    res.send(`
        <!DOCTYPE html>
        <html lang="en" class="scroll-smooth">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>SaaS Billing OpenEnv | Enterprise Dashboard</title>
            <script src="https://cdn.tailwindcss.com"></script>
            <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
            <style>
                body { font-family: 'Inter', sans-serif; }
                .mono { font-family: 'JetBrains Mono', monospace; }
                @keyframes fadeIn {
                    from { opacity: 0; transform: translateY(10px); }
                    to { opacity: 1; transform: translateY(0); }
                }
                .fade-in { animation: fadeIn 0.6s ease-out forwards; }
                .pulse-green {
                    box-shadow: 0 0 0 0 rgba(34, 197, 94, 0.7);
                    animation: pulse-green 2s infinite;
                }
                @keyframes pulse-green {
                    0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(34, 197, 94, 0.7); }
                    70% { transform: scale(1); box-shadow: 0 0 0 10px rgba(34, 197, 94, 0); }
                    100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(34, 197, 94, 0); }
                }
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
                                    <span class="text-[10px] mono text-slate-600">ID: ENV-SB-3000</span>
                                </div>

                                <h1 class="text-3xl font-bold text-white mb-4 leading-tight">Environment Control Center</h1>
                                <p class="text-slate-400 text-sm leading-relaxed mb-8">
                                    Real-time monitoring and control interface for the SaaS Billing Support OpenEnv. 
                                    Designed for high-fidelity agent training and policy evaluation.
                                </p>

                                <div class="grid grid-cols-2 gap-4 mb-8">
                                    <div class="bg-white/5 border border-white/5 p-5 rounded-2xl">
                                        <div class="text-slate-500 text-[10px] font-bold uppercase tracking-widest mb-1">Uptime</div>
                                        <div class="text-xl font-semibold text-white mono">${uptime}s</div>
                                    </div>
                                    <div class="bg-white/5 border border-white/5 p-5 rounded-2xl">
                                        <div class="text-slate-500 text-[10px] font-bold uppercase tracking-widest mb-1">Active Task</div>
                                        <div class="text-xl font-semibold text-blue-400 mono truncate">${activeTask}</div>
                                    </div>
                                    <div class="bg-white/5 border border-white/5 p-5 rounded-2xl">
                                        <div class="text-slate-500 text-[10px] font-bold uppercase tracking-widest mb-1">API Port</div>
                                        <div class="text-xl font-semibold text-white mono">3000</div>
                                    </div>
                                    <div class="bg-white/5 border border-white/5 p-5 rounded-2xl">
                                        <div class="text-slate-500 text-[10px] font-bold uppercase tracking-widest mb-1">Task Count</div>
                                        <div class="text-xl font-semibold text-white mono">${taskCount}</div>
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
                                                <td class="px-6 py-4 text-slate-400 border-b border-white/5">{}</td>
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
                                                <td class="px-6 py-4 text-slate-400 border-b border-white/5">{}</td>
                                                <td class="px-6 py-4 text-slate-500 border-b border-white/5">Enterprise Only</td>
                                            </tr>
                                        </tbody>
                                    </table>

                                    <div class="p-8 space-y-6">
                                        <div>
                                            <h3 class="text-[10px] font-bold text-slate-500 uppercase tracking-widest mb-4">Observation Schema</h3>
                                            <div class="bg-black/40 rounded-2xl p-6 border border-white/5 mono text-[11px] leading-relaxed">
                                                <span class="text-purple-400">"observation"</span>: {<br>
                                                &nbsp;&nbsp;<span class="text-blue-400">"ticket_id"</span>: <span class="text-green-400">"string"</span>,<br>
                                                &nbsp;&nbsp;<span class="text-blue-400">"customer_info"</span>: { <span class="text-slate-500">"tier": "enterprise", ...</span> },<br>
                                                &nbsp;&nbsp;<span class="text-blue-400">"chat_history"</span>: [ <span class="text-slate-500">{ "role": "agent", "content": "..." }</span> ],<br>
                                                &nbsp;&nbsp;<span class="text-blue-400">"available_tools"</span>: [ <span class="text-green-400">"reply", "refund", ...</span> ]<br>
                                                }
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
    `);
  });

  app.post('/reset', (req, res) => {
    const taskId = (req.query.task_id as string) || (req.body.task_id as string) || 'task_1';
    const task = (TASKS as any)[taskId];
    if (!task) {
      return res.status(404).json({ detail: `Task ${taskId} not found` });
    }
    currentTaskId = taskId;
    const obs = env.reset(task.ticket_id, task.customer_id, task.initial_message, task.difficulty);
    res.json(obs);
  });

  app.post('/step', (req, res) => {
    if (!currentTaskId) {
      return res.status(400).json({ detail: 'Environment not reset. Call /reset first.' });
    }
    const action = req.body as Action;
    const [obs, reward] = env.step(action);
    res.json({
      observation: obs,
      reward: reward.value,
      done: reward.is_terminal,
      info: { reason: reward.reason }
    });
  });

  app.get('/state', (req, res) => {
    res.json(env.state());
  });

  app.get('/tasks', (req, res) => {
    res.json(TASKS);
  });

  app.get('/grader', (req, res) => {
    if (!currentTaskId) {
      return res.status(400).json({ detail: 'No active task. Call /reset first.' });
    }
    let score = 0.01;
    if (currentTaskId === 'task_1') score = Grader.grade_task_1(env);
    else if (currentTaskId === 'task_2') score = Grader.grade_task_2(env);
    else if (currentTaskId === 'task_3') score = Grader.grade_task_3(env);
    
    res.json({
      task_id: currentTaskId,
      score: score,
      is_terminal: env.isTerminal
    });
  });

  // Vite middleware for development
  if (process.env.NODE_ENV !== 'production') {
    const vite = await createViteServer({
      server: { middlewareMode: true },
      appType: 'spa',
    });
    app.use(vite.middlewares);
  } else {
    app.use(express.static(path.join(process.cwd(), 'dist')));
    app.get('*', (req, res) => {
      res.sendFile(path.join(process.cwd(), 'dist', 'index.html'));
    });
  }

  app.listen(PORT, '0.0.0.0', () => {
    console.log(`Node server running on http://localhost:${PORT}`);
  });
}

startServer().catch(err => {
  console.error('Failed to start server:', err);
});
