import os
from app import create_app

env = os.getenv("FLASK_ENV", "development")
app = create_app(env)

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    debug = os.getenv("FLASK_DEBUG", "1") == "1"
    print(f"==================================================")
    print(f"  Starting Student Tracker System on http://127.0.0.1:{port}")
    print(f"  Default Admin:   admin   / Admin@123")
    print(f"  Default Faculty: faculty / Faculty@123")
    print(f"==================================================")
    app.run(host="0.0.0.0", port=port, debug=debug)
