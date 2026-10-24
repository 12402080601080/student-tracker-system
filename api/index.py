import sys
import os

# Add root directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app

# Vercel serverless entrypoint
app = create_app(os.getenv("FLASK_ENV", "production"))

# Vercel WSGI entry point
handler = app
