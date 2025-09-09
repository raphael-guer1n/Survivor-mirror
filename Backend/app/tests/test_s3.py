from unittest.mock import patch
from app.utils.s3 import upload_file_to_s3, generate_presigned_url, delete_file_from_s3
import io

def test_upload_file_to_s3():
    with patch("app.utils.s3.s3_client.upload_fileobj") as mock_upload:
        f = io.BytesIO(b"123")
        url = upload_file_to_s3(f, "key", "image/png")
        assert "amazonaws.com" in url
        mock_upload.assert_called_once()

def test_generate_and_delete():
    with patch("app.utils.s3.s3_client.generate_presigned_url", return_value="url") as m:
        assert generate_presigned_url("x") == "url"
    with patch("app.utils.s3.s3_client.delete_object") as m:
        delete_file_from_s3("k")
        m.assert_called_once()
