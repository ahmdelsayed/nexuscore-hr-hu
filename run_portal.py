"""
NexusCore Technologies - Smart HR Operations Hub Launcher
Starts the Bilingual (Arabic / English) Web Portal and opens it in your default web browser.
Supports local execution and Cloud hosting (Render, Railway, etc.).
"""

import os
import sys
import webbrowser
import time
import threading

PORTAL_DIR = os.path.join(os.path.dirname(__file__), "Smart_HR_Operations_Hub", "web_portal")
sys.path.append(PORTAL_DIR)

port = int(os.environ.get("PORT", 8000))
host = os.environ.get("HOST", "0.0.0.0" if os.environ.get("PORT") else "127.0.0.1")
is_cloud = bool(os.environ.get("PORT"))

def open_browser():
    if not is_cloud:
        time.sleep(1.2)
        url = f"http://127.0.0.1:{port}"
        print(f"\n[NexusCore Portal] Opening browser at: {url}")
        webbrowser.open(url)

if __name__ == "__main__":
    import uvicorn
    from app import app

    print("\n" + "="*65)
    print("      NEXUSCORE TECHNOLOGIES - SMART HR OPERATIONS HUB")
    print("      Bilingual Web GUI (Arabic & English) is Starting...")
    print("="*65)
    print(f"\nServer bound to: http://{host}:{port}")
    print("Press CTRL+C to stop the portal.\n")

    threading.Thread(target=open_browser, daemon=True).start()
    uvicorn.run(app, host=host, port=port, log_level="info")
