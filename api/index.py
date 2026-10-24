import os
import sys
from urllib.parse import parse_qs, urlencode

root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from app import create_app

# Flask application instance for Vercel
app = create_app("production")

class VercelQueryPathMiddleware:
    """
    WSGI Middleware to extract original path captured in __path query parameter
    from vercel.json rewrite rule and restore standard PATH_INFO for Flask routing.
    """
    def __init__(self, wsgi_app):
        self.wsgi_app = wsgi_app

    def __call__(self, environ, start_response):
        qs = environ.get("QUERY_STRING", "")
        if "__path=" in qs:
            params = parse_qs(qs, keep_blank_values=True)
            if "__path" in params:
                raw_path = params.pop("__path")[0]
                # Ensure leading slash and remove duplicate slashes
                clean_path = "/" + raw_path.lstrip("/")
                environ["PATH_INFO"] = clean_path
                environ["QUERY_STRING"] = urlencode(params, doseq=True)

        return self.wsgi_app(environ, start_response)

# Attach middleware to WSGI application
app.wsgi_app = VercelQueryPathMiddleware(app.wsgi_app)
