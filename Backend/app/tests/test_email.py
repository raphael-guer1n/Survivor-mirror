from unittest.mock import patch
from app.utils.email import send_verification_email

def test_send_email():
    with patch("smtplib.SMTP") as mock_smtp, patch("builtins.open", create=True) as mock_open:
        mock_open.return_value.__enter__.return_value.read.return_value = "code={{ code }}"
        send_verification_email("me@example.com", "111111")
        mock_smtp.assert_called_once()
