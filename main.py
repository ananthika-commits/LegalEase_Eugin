"""
LegalEase FastAPI Backend Application
Entry point for the REST API powering AI-driven legal document generation.
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from routes import router

app = FastAPI(
    title="LegalEase API",
    description="AI-Powered Legal Document Generator API leveraging Google GenAI.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS for local Streamlit frontend and API clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins in development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include document generation router
app.include_router(router)

LANDING_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LegalEase | AI-Powered Legal Document Generator</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; }
        body { background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%); color: #f8fafc; min-height: 100vh; display: flex; align-items: center; justify-content: center; padding: 20px; }
        .card { background: rgba(30, 41, 59, 0.9); border: 1px solid #3b82f6; border-radius: 16px; max-width: 680px; width: 100%; padding: 40px; box-shadow: 0 20px 40px rgba(0,0,0,0.5); text-align: center; }
        .badge { display: inline-flex; align-items: center; gap: 6px; background: rgba(16, 185, 129, 0.2); color: #34d399; border: 1px solid #059669; padding: 6px 14px; border-radius: 9999px; font-size: 0.85rem; font-weight: 600; margin-bottom: 20px; }
        .badge-dot { width: 8px; height: 8px; background: #10b981; border-radius: 50%; display: inline-block; }
        h1 { font-size: 2.2rem; margin-bottom: 12px; color: #ffffff; font-family: 'Georgia', serif; }
        h1 span { color: #60a5fa; }
        p.subtitle { color: #94a3b8; font-size: 1.05rem; margin-bottom: 30px; line-height: 1.5; }
        .btn-group { display: flex; flex-direction: column; gap: 14px; margin-bottom: 30px; }
        .btn { display: block; padding: 14px 24px; border-radius: 10px; font-size: 1.05rem; font-weight: 600; text-decoration: none; transition: all 0.2s ease; }
        .btn-primary { background: #2563eb; color: #ffffff; border: 1px solid #3b82f6; box-shadow: 0 4px 14px rgba(37, 99, 235, 0.4); }
        .btn-primary:hover { background: #1d4ed8; transform: translateY(-2px); }
        .btn-secondary { background: #1e293b; color: #cbd5e1; border: 1px solid #475569; }
        .btn-secondary:hover { background: #334155; color: #ffffff; }
        .info-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; text-align: left; background: rgba(15, 23, 42, 0.6); padding: 18px; border-radius: 10px; border: 1px solid #334155; }
        .info-item { font-size: 0.85rem; }
        .info-item strong { color: #38bdf8; display: block; margin-bottom: 2px; }
        .info-item span { color: #cbd5e1; }
        .auto-redirect { font-size: 0.85rem; color: #64748b; margin-top: 15px; }
        .auto-redirect a { color: #38bdf8; text-decoration: underline; cursor: pointer; }
    </style>
</head>
<body>
    <div class="card">
        <div class="badge">
            <span class="badge-dot"></span> Backend API Status: Online (Port 8000)
        </div>
        <h1>⚖️ Legal<span>Ease</span></h1>
        <p class="subtitle">
            Welcome to the LegalEase Backend API. To create, edit, preview, and export legal documents, open the interactive <strong>Streamlit Web Application</strong>.
        </p>
        
        <div class="btn-group">
            <a href="http://localhost:8501" class="btn btn-primary" id="launch-btn">
                🚀 Launch LegalEase Web App (Port 8501)
            </a>
            <a href="/docs" class="btn btn-secondary">
                📖 View Interactive API Documentation (Swagger)
            </a>
        </div>

        <div class="info-grid">
            <div class="info-item">
                <strong>🖥️ Frontend Web App:</strong>
                <span><a href="http://localhost:8501" style="color:#93c5fd;">http://localhost:8501</a></span>
            </div>
            <div class="info-item">
                <strong>⚙️ REST API Endpoint:</strong>
                <span><code>POST /generate</code></span>
            </div>
            <div class="info-item">
                <strong>🤖 AI Core Engine:</strong>
                <span>Google GenAI SDK (gemini-1.5-pro)</span>
            </div>
            <div class="info-item">
                <strong>📑 Export Formats:</strong>
                <span>.DOCX, .PDF, .TXT</span>
            </div>
        </div>

        <p class="auto-redirect" id="redirect-msg">
            Redirecting to Web App in <span id="timer">4</span> seconds... <a onclick="cancelRedirect()">[Cancel]</a>
        </p>
    </div>

    <script>
        let timeLeft = 4;
        let cancelled = false;
        const timerEl = document.getElementById('timer');
        const msgEl = document.getElementById('redirect-msg');

        function cancelRedirect() {
            cancelled = true;
            msgEl.innerHTML = "Auto-redirect cancelled. Click the launch button above anytime.";
        }

        const interval = setInterval(() => {
            if (cancelled) {
                clearInterval(interval);
                return;
            }
            timeLeft--;
            if (timerEl) timerEl.textContent = timeLeft;
            if (timeLeft <= 0) {
                clearInterval(interval);
                window.location.href = "http://localhost:8501";
            }
        }, 1000);
    </script>
</body>
</html>
"""


@app.get("/", summary="Root Portal & Health Check")
async def root(request: Request):
    """
    Root endpoint verifying API server status.
    If requested by a web browser, displays the interactive portal landing page with
    direct launch to the Streamlit frontend.
    If requested by an API client or test suite, returns JSON metadata.
    """
    accept = request.headers.get("accept", "")
    # Check if a web browser requested the page (browsers send text/html first)
    if "text/html" in accept and not accept.startswith("*/*"):
        return HTMLResponse(content=LANDING_HTML)

    return {
        "message": "Welcome to LegalEase: AI-Powered Legal Document Generator API",
        "status": "online",
        "documentation": "/docs",
        "version": "1.0.0",
        "frontend_url": "http://localhost:8501"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
