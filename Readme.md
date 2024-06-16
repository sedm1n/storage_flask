# File Storage with HTTP Access

This project implements a file storage system using Flask, allowing authenticated users to upload, download, and delete files via HTTP. Authentication is required for uploading and deleting files.

## Features

- **Upload files**: Authenticated users can upload files.
- **Download files**: Files can be downloaded by anyone.
- **Delete files**: Authenticated users can delete files.

## Getting Started

### Prerequisites

- Python 3.11+
- Flask
- Flask-Migrate

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/sedm1n/storage_flask.git
   cd storage_flask/
```

Create and activate a virtual environment:

```bash

python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
```
Install the required packages:

```bash

pip install -r requirements.txt
```

Rename the example environment configuration file:


```bash

mv example.flaskenv .flaskenv
```

Database Setup
Initialize and apply migrations to set up the database:

```bash

flask db init
flask db migrate
flask db upgrade
```

By default, the application uses SQLite for the database.

Running the Application
To start the application in development mode, use:

```bash

flask run
```
The application will be available at http://127.0.0.1:5000.

Usage
Uploading Files
To upload a file, use the following curl command:

```bash

curl -u username:password -F "file=@filename" http://127.0.0.1:5000/upload
```
Replace username and password with your credentials and filename with the path to the file you want to upload.

Downloading Files
Files can be downloaded by accessing the URL http://127.0.0.1:5000/download/<filehash>, where <filehash> is the name of the file.

Deleting Files
To delete a file, use the following curl command:

```bash
curl -u username:password -X DELETE http://127.0.0.1:5000/delete/<filehash>
```

Replace username and password with your credentials and <filename> with the name of the file you want to delete.

Contributing
Contributions are welcome! Please open an issue or submit a pull request.

License
This project is licensed under the MIT License.