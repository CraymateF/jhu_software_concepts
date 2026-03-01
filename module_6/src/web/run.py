"""
Flask entrypoint for the GradCafe web service.
Binds to 0.0.0.0:8080 as required by the Docker deployment.
"""
import os
from app import create_app

application = create_app()

if __name__ == "__main__":
    debug_mode = os.getenv("FLASK_DEBUG", "false").lower() == "true"
    application.run(host="0.0.0.0", port=8080, debug=debug_mode)
