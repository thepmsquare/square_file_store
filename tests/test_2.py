import io

from fastapi.testclient import TestClient

from square_file_store.main import (
    app,
)

client = TestClient(app)


def test_read_main():
    #################################
    # upload file test case
    #################################

    file_content = b"Hello, this is the content of the file."
    file_name = "example.txt"

    # Create an in-memory byte stream
    file = io.BytesIO(file_content)

    files = {"file": (file_name, file, "multipart/form-data")}

    # Make the request
    response = client.post("/upload_file/v0", files=files)

    # Assert the response status code
    assert response.status_code == 201
    upload_response = response.json()
    assert "data" in upload_response and "main" in upload_response["data"]
