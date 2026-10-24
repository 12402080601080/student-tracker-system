import os
from app import create_app

# Vercel entrypoint: Uses production config if running on Vercel
env = "production" if os.getenv("VERCEL") else os.getenv("FLASK_ENV", "development")
app = create_app(env)

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
