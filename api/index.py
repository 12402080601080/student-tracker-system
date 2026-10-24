import os
import sys

# Add project root directory to sys.path
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from app import create_app
from flask import redirect, url_for, request, jsonify

# Flask application instance for Vercel
app = create_app("production")

@app.route("/debug")
def debug_info():
    """Diagnostic endpoint to inspect Vercel environment and routing headers."""
    return jsonify({
        "path": request.path,
        "full_path": request.full_path,
        "url": request.url,
        "environ_PATH_INFO": request.environ.get("PATH_INFO"),
        "environ_SCRIPT_NAME": request.environ.get("SCRIPT_NAME"),
        "environ_REQUEST_URI": request.environ.get("REQUEST_URI"),
        "environ_RAW_URI": request.environ.get("RAW_URI"),
        "headers": dict(request.headers),
    })

@app.route("/api/index")
@app.route("/api/index/")
def vercel_index_alias():
    """Fallback handler in case PATH_INFO /api/index reaches Flask router."""
    return redirect(url_for("auth.login"))
