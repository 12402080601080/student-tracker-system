import os
import sys

# Add project root directory to sys.path
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from app import create_app
from flask import redirect, url_for

# Flask application instance for Vercel
app = create_app("production")

@app.route("/api/index")
@app.route("/api/index/")
def vercel_index_alias():
    """Fallback handler in case PATH_INFO /api/index reaches Flask router."""
    return redirect(url_for("auth.login"))

class VercelPathFixMiddleware:
    """
    WSGI Middleware to map Vercel serverless request paths to Flask routes.
    Vercel sets HTTP_X_MATCHED_PATH (or HTTP_X_FORWARDED_URI) to the original request path.
    If the incoming PATH_INFO was rewritten to /api/index, restore the intended path.
    """
    def __init__(self, wsgi_app):
        self.wsgi_app = wsgi_app

    def __call__(self, environ, start_response):
        # 1. Check Vercel's original matched path header
        matched_path = environ.get("HTTP_X_MATCHED_PATH") or environ.get("HTTP_X_FORWARDED_URI")
        if matched_path:
            clean_path = matched_path.split("?")[0]
            if clean_path:
                environ["PATH_INFO"] = clean_path
        else:
            path_info = environ.get("PATH_INFO", "")
            if path_info in ["/api/index", "/api/index/"]:
                environ["PATH_INFO"] = "/"
            elif path_info.startswith("/api/index/"):
                environ["PATH_INFO"] = path_info[len("/api/index"):] or "/"

        return self.wsgi_app(environ, start_response)

# Wrap WSGI app with path normalization middleware
app.wsgi_app = VercelPathFixMiddleware(app.wsgi_app)
