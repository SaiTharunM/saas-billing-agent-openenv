# Running SaaS Billing Support OpenEnv Locally

This project is a **Full-Stack Application** with both Python (FastAPI) and Node.js (Express) implementations. The `index.html` file in the root is **not** the main entry point; the UI is generated dynamically by the backend server.

## Option 1: Run with Python (Recommended for Submission)

This is the version that will be used for the competition and Hugging Face Spaces.

1.  **Install Python Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

2.  **Run the Server:**
    ```bash
    python app.py
    ```

3.  **Access the Dashboard:**
    Open your browser and go to `http://localhost:7860`.

4.  **Run the Baseline Test:**
    In a separate terminal, run:
    ```bash
    python baseline.py
    ```

## Option 2: Run with Node.js (Development Mode)

This version is used for the AI Studio preview.

1.  **Install Node.js Dependencies:**
    ```bash
    npm install
    ```

2.  **Run the Server:**
    ```bash
    npm run dev
    ```

3.  **Access the Dashboard:**
    Open your browser and go to `http://localhost:3000`.

## Why `index.html` shows a blank screen?

The `index.html` file is a shell for a React application that requires a build step or a development server (like Vite) to run. Since the main logic of this environment is handled by the backend servers (`app.py` or `server.ts`), opening `index.html` directly with "Live Server" will not connect to the environment logic or the Tailwind CSS configuration.

**Always run the backend server to see the full interface.**
