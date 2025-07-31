from app import app  # Import the Flask app from app.py
import logging
import os

if __name__ == "__main__":
    # Set logging level
    logging.basicConfig(level=logging.INFO)

    # Use environment port if available (Render sets $PORT), else fallback to 5006
    port = int(os.environ.get("PORT", 5006))
    host = "0.0.0.0"  # Required for Render & external access

    logging.info(f"Starting Flask app on http://{host}:{port}")

    # Start the app
    app.run(host=host, port=port, debug=True)

