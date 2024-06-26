import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
      SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL"
    ) or "sqlite:///" + os.path.join(basedir, "db.sqlite")
      UPLOAD_FOLDER = os.path.join(basedir, 'storage')
      