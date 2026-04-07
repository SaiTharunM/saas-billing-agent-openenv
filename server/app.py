from fastapi import FastAPI
import uvicorn

app = FastAPI()

@app.get("/")
def home():
    return {"message": "SaaS Billing Support Running 🚀"}

# ✅ REQUIRED main() function
def main():
    uvicorn.run("server.app:app", host="0.0.0.0", port=7860)

# ✅ REQUIRED for OpenEnv
if __name__ == "__main__":
    main()