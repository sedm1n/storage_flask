from app import app
import sqlalchemy as sa
import sqlalchemy.orm as so
from app import  db
from app.models import User, FileHash

# app = create_app()


@app.shell_context_processor
def make_shell_context():
    return {'sa': sa, 'so': so, 'db': db, 'User': User, 'FileHash': FileHash}