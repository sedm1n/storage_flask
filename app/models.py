from werkzeug.security import generate_password_hash, check_password_hash

from typing import Optional
import sqlalchemy as sa
import sqlalchemy.orm as so
from app import db


class User(db.Model):
    """
    User database model.
    """

    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    """Primary key for the user."""

    username: so.Mapped[str] = so.mapped_column(sa.String(120), index=True, unique=True)
    

    password_hash: so.Mapped[Optional[str]] = so.mapped_column(sa.String(256))
    

    file_hash: so.WriteOnlyMapped["FileHash"] = so.relationship(back_populates="user")
    """Relationship to the file hashes associated with the user."""

    def set_password(self, password: str):
        """
        Set the password for the user.

        Args:
            password (str): The password to set.
        """
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str):
        """
        Check if the given password matches the stored password hash.

        Args:
            password (str): The password to check.

        Returns:
            bool: True if the password matches, False otherwise.
        """
        return check_password_hash(self.password_hash, password)


class FileHash(db.Model):
    """
    File hash database model.
    """

    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    """Primary key for the file hash."""

    file_hash: so.Mapped[str] = so.mapped_column(sa.String(256), index=True)
    

    user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(User.id), index=True)
    """Foreign key to the user associated with the file hash."""

    user: so.Mapped[User] = so.relationship(back_populates="file_hash")
    """Relationship to the user associated with the file hash."""

