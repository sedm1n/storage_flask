import hashlib
import os
from typing import Tuple
import sqlalchemy as sa
from flask import  Response, jsonify, request, send_file
from app import app, db, auth
from app.models import FileHash, User


@auth.verify_password
def verify_password(username, password):
    """
    Verify the username and password for authentication.

    Args:
        username (str): The username.
        password (str): The password.

    Returns:
        User: The user object if the authentication is successful, False otherwise.
    """
    
    user = User.query.filter_by(username=username).first()
    app.logger.debug(user.username)
    app.logger.debug(user.check_password(password))
   
    if not user or not user.check_password(password):
        return False
    
    app.logger.info(f"User {user.username} authenticated successfully")
    return user

def get_file_path(file_hash: str) -> str:
    """
    Returns the path to the file in local storage.

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
    Uploads the file to the server.

    Returns:
        Tuple[Response, int]: A tuple containing the response and status code.
    """
    if "file" not in request.files:
        return jsonify({"message": "No file part"}), 400

    file = request.files["file"]
    app.logger.debug(file.name)
    try:
        file_content = file.read()
    except Exception as e:
        return jsonify({"message": "Error reading file: {}".format(str(e))}), 400

    file_hash = hashlib.sha256(file_content).hexdigest()  
    file_path = get_file_path(file_hash=file_hash)
    dir_path  = os.path.dirname(file_path)
    
    app.logger.debug(file_path)
    app.logger.debug(dir_path)

    try:
        os.makedirs(dir_path, exist_ok=True)
    except Exception as e:
        return jsonify({"message": "Error creating directory: {}".format(str(e))}), 500

    try:
        with open(file_path, "wb") as f:
            f.write(file_content)
        
    except Exception as e:
        app.logger.exception(str(e))
        return jsonify({"message": "Error writing file: {}".format(str(e))}), 500

    try:
        data = FileHash(file_hash=file_hash, user=auth.current_user())
        db.session.add(data)
        db.session.commit()
        app.logger.info("File added to database")
    except Exception as e:
        app.logger.exception(str(e))
        return jsonify({"message": "Error saving to database: {}".format(str(e))}), 500

    return jsonify({"File added successfully, hash": file_hash}), 201


@app.route("/download/<file_hash>", methods=["GET"])
def download_file(file_hash: str) -> Tuple[Response, int]:
    """
    Downloads the file from the server.

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
    Deletes the file from the server. 
    Args:
        file_hash (str): Hash of the file to be deleted.

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
        app.logger.exception(str(e))
        return jsonify({"message": "Error deleting file: {}".format(str(e))}), 500
    
    try:
        db.session.delete(file_record)
        db.session.commit()
        app.logger.info("File deleted from database")
        return jsonify({"message": "File deleted"}), 200
    except Exception as e:
        app.logger.exception(str(e))
        return jsonify({"message": "Error deleting from database: {}".format(str(e))}), 500
    

    



