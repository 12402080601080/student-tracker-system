import os
import sys
import traceback

root_dir = os.path.dirname(os.path.abspath(__file__))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

flask_app = None
init_error = None

try:
    from app import create_app
    env = "production" if os.getenv("VERCEL") else os.getenv("FLASK_ENV", "development")
    flask_app = create_app(env)
except Exception:
    init_error = traceback.format_exc()

def app(environ, start_response):
    """Crash-proof WSGI handler for Vercel serverless."""
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

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    if flask_app:
        flask_app.run(host="0.0.0.0", port=port)
