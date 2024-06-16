import hashlib
import os
from typing import Tuple
import sqlalchemy as sa
from flask import  Response, jsonify, request, send_file
from app import app, db, auth
from app.models import FileHash, User


@auth.verify_password
def verify_password(username, password):
    user = User.query.filter_by(username=username).first()
    if not user or not user.check_password(password):
        return False
    
    return user

def get_file_path(file_hash: str) -> str:
    """
    Возвращает путь к файлу в локальном хранилище.

    Args:
        file_hash (str): The hash of the file.

    Returns:
        str: The path of the file.
    """
    subdir = file_hash[:2]
    return os.path.join(app.config["UPLOAD_FOLDER"], subdir, file_hash)


@app.route("/upload", methods=["POST"])
@auth.login_required
def upload_file() -> Tuple[Response, int]:
    """
    Загружает файл на сервер.

    Returns:
        Tuple[Response, int]: A tuple containing the response and status code.
    """
    if "file" not in request.files:
        return jsonify({"message": "No file part"}), 400

    file = request.files["file"]

    try:
        file_content = file.read()
    except Exception as e:
        return jsonify({"message": "Error reading file: {}".format(str(e))}), 400

    file_hash = hashlib.sha256(file_content).hexdigest()
    
    file_path = get_file_path(file_hash=file_hash)
    dir_path  = os.path.dirname(file_path)
    try:
        os.makedirs(dir_path, exist_ok=True)
    except Exception as e:
        return jsonify({"message": "Error creating directory: {}".format(str(e))}), 500

    try:
        with open(file_path, "wb") as f:
            f.write(file_content)
    except Exception as e:
        return jsonify({"message": "Error writing file: {}".format(str(e))}), 500

    try:
        data = FileHash(file_hash=file_hash, user=auth.current_user())
        db.session.add(data)
        db.session.commit()
    except Exception as e:
        return jsonify({"message": "Error saving to database: {}".format(str(e))}), 500

    return jsonify({"File added successfully, hash": file_hash}), 201


@app.route("/download/<file_hash>", methods=["GET"])
def download_file(file_hash: str) -> Tuple[Response, int]:
    """
    Позволяет скачать файл 

    Args:
        file_hash (str): на входе хэш скачиваемого файла.

    Returns:
        Tuple[Response, int]: A tuple containing the response and status code.
    """
    file_path = get_file_path(file_hash=file_hash)

    if not os.path.exists(get_file_path(file_hash=file_hash)):
        return jsonify({"message": "File not found"}), 404

    return send_file(file_path), 200


@app.route("/delete/<file_hash>", methods=["DELETE"])
@auth.login_required
def delete_file(file_hash: str) -> Tuple[Response, int]:
    """
    Удаляет файл найденный в локальном хранилище. Файл удаляется только если он
      принадлежит текущему авторизованному пользователю.
    Так же удаляется запись о хэше в базе данных.

    Args:
        file_hash (str): На входе хэш удаляемого файла.

    Returns:
        Tuple[Response, int]: A tuple containing the response and status code.
    """
    file_path = get_file_path(file_hash=file_hash)

    if not os.path.exists(file_path):
        return jsonify({"message": "File not found"}), 404

    file_record = FileHash.query.filter_by(
        file_hash=file_hash, user=auth.current_user()
    ).first()

    if not file_record:
        return jsonify({"message": "File not found"}), 404

    try:
        os.remove(file_path)
    except Exception as e:
        return jsonify({"message": "Error deleting file: {}".format(str(e))}), 500
    
    try:
        db.session.delete(file_record)
        db.session.commit()

        return jsonify({"message": "File deleted"}), 200
    except Exception as e:
        return jsonify({"message": "Error deleting from database: {}".format(str(e))}), 500
    

    



