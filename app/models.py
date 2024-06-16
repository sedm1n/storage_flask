from werkzeug.security import generate_password_hash, check_password_hash

from typing import Optional
import sqlalchemy as sa
import sqlalchemy.orm as so
from app import db


class User(db.Model):
      id: so.Mapped[int] = so.mapped_column(primary_key=True)
      username: so.Mapped[str] = so.mapped_column(sa.String(120), index=True, unique=True)
      password_hash: so.Mapped[Optional[str]] = so.mapped_column(sa.String(256))
      file_hash: so.WriteOnlyMapped['FileHash'] = so.relationship(
            back_populates='user'
      )

      def set_password(self, password:str):
            self.password_hash = generate_password_hash(password)

      def check_password(self, password:str):
            return check_password_hash(self.password_hash, password)
      

class FileHash(db.Model):
      id: so.Mapped[int] = so.mapped_column(primary_key=True)
      file_hash: so.Mapped[str] = so.mapped_column(sa.String(256), index=True)
      user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(User.id), index=True)
      user: so.Mapped[User] = so.relationship(back_populates='file_hash')