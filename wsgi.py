import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))

from app import app, db, seed_if_empty
from models import Usuario
from werkzeug.security import generate_password_hash


@app.before_request
def _init_db_once():
    """Inicializa tablas y seed en el primer request, no al importar."""
    if not getattr(app, "_db_ready", False):
        with app.app_context():
            db.create_all()
            seed_if_empty()
            _emergency_reset()
        app._db_ready = True


def _emergency_reset():
    """
    Si ADMIN_RESET_PASS está definido como env var, actualiza la contraseña
    del usuario 'admin' y loguea el evento. Elimina la env var después de usarla.
    """
    new_pass = os.environ.get("ADMIN_RESET_PASS")
    if not new_pass:
        return
    u = Usuario.query.filter_by(user="admin").first()
    if u:
        u.pass_ = generate_password_hash(new_pass)
        db.session.commit()
        app.logger.warning("⚠️  Admin password was reset via ADMIN_RESET_PASS env var. Remove it from Render now.")


if __name__ == "__main__":
    app.run()
