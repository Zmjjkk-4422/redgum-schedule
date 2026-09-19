"""Application factory for the Redgum Tutoring scheduling system."""
import os

from flask import Flask, render_template

from .db import init_app as init_db_app
from .seed import register_commands


def create_app(config_name=None, test_config=None):
    app = Flask(__name__)

    config_name = config_name or os.getenv("FLASK_CONFIG", "dev")
    from config import config as config_map

    app.config.from_object(config_map[config_name])
    if test_config:
        app.config.update(test_config)

    init_db_app(app)
    register_commands(app)

    from .routes.students import bp as students_bp
    from .routes.sessions import bp as sessions_bp
    from .routes.schedule import bp as schedule_bp

    app.register_blueprint(students_bp)
    app.register_blueprint(sessions_bp)
    app.register_blueprint(schedule_bp)

    @app.route("/")
    def index():
        from . import models

        return render_template(
            "index.html",
            student_count=models.count_students(),
            tutor_count=models.count_tutors(),
            session_count=models.count_sessions(),
        )

    return app
