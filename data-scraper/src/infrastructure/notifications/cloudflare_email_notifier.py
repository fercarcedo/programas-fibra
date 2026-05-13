from domain.notifications.email_notifier import EmailNotifier
from infrastructure.notifications.templates.alert_email import ALERT_EMAIL_HTML
from js import Blob
from pyodide.ffi import to_js
from workers import import_from_javascript
import html

class CloudflareEmailNotifier(EmailNotifier):
    def __init__(self, env):
        self._send_email = env.SEND_EMAIL
        self._from_addr = env.ALERT_FROM
        self._to_addr = env.ALERT_RECIPIENT

    async def send_alert(self, subject: str, body: str) -> None:
        raw = self._build_raw_email(subject, body)
        blob = Blob.new(to_js([raw.encode('utf-8')]))
        cf_email = import_from_javascript('cloudflare:email')
        msg = cf_email.EmailMessage.new(self._from_addr, self._to_addr, blob.stream())
        await self._send_email.send(msg)

    def _build_raw_email(self, subject: str, body: str) -> str:
        html_body = ALERT_EMAIL_HTML.format(body=html.escape(body))
        return (
            f"From: {self._from_addr}\r\n"
            f"To: {self._to_addr}\r\n"
            f"Subject: {subject}\r\n"
            f"Content-Type: text/html; charset=utf-8\r\n"
            f"\r\n"
            f"{html_body}"
        )
