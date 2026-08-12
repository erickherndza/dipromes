import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))

from app import app, db, seed_if_empty

with app.app_context():
    db.create_all()
    seed_if_empty()

if __name__ == "__main__":
    app.run()
