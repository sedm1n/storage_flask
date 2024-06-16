import os
import tempfile
import pytest
from app import app, db
from app.models import User, FileHash

@pytest.fixture
def app_fixture():
    db_fd, db_path = tempfile.mkstemp()
    upload_folder = tempfile.mkdtemp()
    print(upload_folder)

    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_path
    app.config['UPLOAD_FOLDER'] = upload_folder

    with app.app_context():
        db.create_all()
        if not User.query.filter_by(username='testuser').first():
            user = User(username='testuser')
            user.set_password('testpassword')
            db.session.add(user)
            db.session.commit()

    yield app

    os.close(db_fd)
    os.unlink(db_path)
    # os.rmdir(upload_folder)

@pytest.fixture
def client(app_fixture):
    return app_fixture.test_client()

def test_upload_file(client):
    with open('testfile.txt', 'w') as f:
        f.write('This is a test file.')

    with open('testfile.txt', 'rb') as f:
        response = client.post('/upload', data={'file': f}, headers={'Authorization': 'Basic dGVzdHVzZXI6dGVzdHBhc3N3b3Jk'})
    
    print(response.get_json())
    assert response.status_code == 201
    
    os.remove('testfile.txt')

def test_download_file(client):
    # First, upload a file
    with open('testfile.txt', 'w') as f:
        f.write('This is a test file.')

    with open('testfile.txt', 'rb') as f:
        upload_response = client.post('/upload', data={'file': f}, headers={'Authorization': 'Basic dGVzdHVzZXI6dGVzdHBhc3N3b3Jk'})

    file_hash = upload_response.get_json()['hash']

    # Now, download the file
    download_response = client.get(f'/download/{file_hash}')

    assert download_response.status_code == 200
    

    os.remove('testfile.txt')

def test_delete_file(client):
    # First, upload a file
    with open('testfile.txt', 'w') as f:
        f.write('This is a test file.')

    with open('testfile.txt', 'rb') as f:
        upload_response = client.post('/upload', data={'file': f}, headers={'Authorization': 'Basic dGVzdHVzZXI6dGVzdHBhc3N3b3Jk'})
    print(upload_response.get_json())
    file_hash = upload_response.get_json()['hash']

    # Now, delete the file
    delete_response = client.delete(f'/delete/{file_hash}', headers={'Authorization': 'Basic dGVzdHVzZXI6dGVzdHBhc3N3b3Jk'})

    assert delete_response.status_code == 200
   
