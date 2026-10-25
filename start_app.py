import subprocess
import os
import sys
import time
import signal

try:
    if sys.stdout.encoding != 'utf-8':
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

import shutil

cwd = os.path.dirname(os.path.abspath(__file__))

# Resolve node executable dynamically from PATH or common Windows locations
node_exe = shutil.which("node")
if not node_exe:
    candidates = [
        r"C:\Program Files\nodejs\node.exe",
        r"C:\Program Files (x86)\nodejs\node.exe",
        os.path.expandvars(r"%LOCALAPPDATA%\Programs\node\node.exe"),
    ]
    for candidate in candidates:
        if os.path.isfile(candidate):
            node_exe = candidate
            break

if not node_exe:
    node_exe = "node"

server_script = os.path.join(cwd, "server", "src", "index.ts")
vite_js = os.path.join(cwd, "client", "node_modules", "vite", "bin", "vite.js")

env = os.environ.copy()

print("=" * 60)
print("[ClaimX AI] Launching Crop Insurance Agentic System")
print("=" * 60)

backend_proc = subprocess.Popen(
    [node_exe, "--experimental-strip-types", server_script],
    cwd=os.path.join(cwd, "server"),
    env=env
)
print("[OK] Backend API Server started on http://localhost:3001")

client_proc = subprocess.Popen(
    [node_exe, vite_js, "--host", "0.0.0.0", "--port", "5173"],
    cwd=os.path.join(cwd, "client"),
    env=env
)
print("[OK] Frontend Client started on http://localhost:5173")
print("=" * 60)
print("[ClaimX AI] Application is live and listening for requests.")
sys.stdout.flush()

def cleanup(sig, frame):
    print("Stopping ClaimX AI servers...")
    backend_proc.terminate()
    client_proc.terminate()
    sys.exit(0)

signal.signal(signal.SIGINT, cleanup)
signal.signal(signal.SIGTERM, cleanup)

try:
    while True:
        if backend_proc.poll() is not None:
            print(f"Backend process exited with code {backend_proc.returncode}.")
            break
        if client_proc.poll() is not None:
            print(f"Frontend process exited with code {client_proc.returncode}.")
            break
        time.sleep(1)
except KeyboardInterrupt:
    cleanup(None, None)
