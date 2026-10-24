import os
import sys
import traceback

# Add project root directory to sys.path so modules in app/ can be imported
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

cwd = os.getcwd()
if cwd not in sys.path:
    sys.path.insert(0, cwd)

flask_app = None
init_error = None

try:
    from app import create_app
    flask_app = create_app("production")
except Exception:
    init_error = traceback.format_exc()

def app(environ, start_response):
    """Crash-proof WSGI handler for Vercel serverless functions."""
    if init_error:
        response_body = f"STARTUP ERROR:\n\n{init_error}".encode("utf-8")
        status = "500 Internal Server Error"
        headers = [
            ("Content-Type", "text/plain; charset=utf-8"),
            ("Content-Length", str(len(response_body)))
        ]
        start_response(status, headers)
        return [response_body]

    try:
        return flask_app(environ, start_response)
    except Exception:
        err_msg = f"RUNTIME ERROR:\n\n{traceback.format_exc()}".encode("utf-8")
        status = "500 Internal Server Error"
        headers = [
            ("Content-Type", "text/plain; charset=utf-8"),
            ("Content-Length", str(len(err_msg)))
        ]
        start_response(status, headers)
        return [err_msg]
