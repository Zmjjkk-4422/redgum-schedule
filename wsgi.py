"""WSGI entry point.

Local development:  python wsgi.py
Flask CLI:          flask --app wsgi run
Production:         gunicorn wsgi:app
"""
from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
