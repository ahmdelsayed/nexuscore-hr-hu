import os
import sys

# Ensure root and portal directories are on sys.path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
PORTAL_DIR = os.path.join(ROOT_DIR, "Smart_HR_Operations_Hub", "web_portal")
SIMULATOR_DIR = os.path.join(ROOT_DIR, "Smart_HR_Operations_Hub", "simulator")
TEMPLATES_DIR = os.path.join(ROOT_DIR, "Smart_HR_Operations_Hub", "templates")

for p in [ROOT_DIR, PORTAL_DIR, SIMULATOR_DIR, TEMPLATES_DIR]:
    if p not in sys.path:
        sys.path.insert(0, p)

try:
    from Smart_HR_Operations_Hub.web_portal.app import app
except Exception as e:
    import traceback
    err_trace = traceback.format_exc()
    from fastapi import FastAPI
    from fastapi.responses import HTMLResponse
    app = FastAPI(title="NexusCore Diagnostic")
    
    @app.get("/{full_path:path}", response_class=HTMLResponse)
    def catch_all(full_path: str = ""):
        return f"""
        <!DOCTYPE html>
        <html>
        <head><title>NexusCore Deployment Diagnostic</title></head>
        <body style="font-family: monospace; padding: 2rem; background: #080C14; color: #F43F5E;">
            <h1>Startup Diagnostic Log</h1>
            <p><strong>Error:</strong> {str(e)}</p>
            <pre style="background: #111A2E; padding: 1.5rem; border-radius: 8px; color: #CBD5E1; overflow: auto; border: 1px solid rgba(255,255,255,0.1);">{err_trace}</pre>
        </body>
        </html>
        """
