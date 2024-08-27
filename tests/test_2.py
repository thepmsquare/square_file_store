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
    response = client.post("/upload_file", files=files)

    # Assert the response status code
    assert response.status_code == 200
    upload_response = response.json()
    assert (
        "additional_info" in upload_response
        and "FileStorageToken" in upload_response["additional_info"]
    )
