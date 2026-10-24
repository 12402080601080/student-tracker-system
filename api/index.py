import os
import sys

root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from app import create_app
from flask import request, jsonify

app = create_app("production")

@app.route("/api/index", methods=["GET", "POST"])
@app.route("/api/index/", methods=["GET", "POST"])
def inspect_vercel():
    env_data = {k: str(v) for k, v in request.environ.items() if isinstance(v, (str, int, float, bool))}
    return jsonify(env_data)
