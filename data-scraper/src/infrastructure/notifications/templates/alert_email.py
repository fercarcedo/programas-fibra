ALERT_EMAIL_HTML = """\
<!DOCTYPE html>
<html>
<head><meta charset="utf-8"></head>
<body style="margin:0;padding:0;background:#f5f5f5;font-family:Arial,sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background:#f5f5f5;">
    <tr>
      <td align="center" style="padding:32px 16px;">
        <table width="560" cellpadding="0" cellspacing="0" style="background:#ffffff;border-radius:8px;overflow:hidden;box-shadow:0 2px 8px rgba(0,0,0,0.08);">
          <tr>
            <td style="background:#DC3545;padding:20px 32px;">
              <span style="color:#ffffff;font-size:18px;font-weight:bold;">Programas Fibra</span>
            </td>
          </tr>
          <tr>
            <td style="padding:24px 32px 0;">
              <span style="background:#FFF3CD;color:#856404;border:1px solid #FFEAA7;border-radius:4px;padding:6px 12px;font-size:13px;font-weight:bold;">&#9888; Data Scraper Alert</span>
            </td>
          </tr>
          <tr>
            <td style="padding:20px 32px 32px;">
              <pre style="background:#f8f9fa;border-left:4px solid #DC3545;padding:16px;font-family:monospace;font-size:13px;line-height:1.5;white-space:pre-wrap;word-break:break-word;margin:0;border-radius:0 4px 4px 0;">{body}</pre>
            </td>
          </tr>
        </table>
      </td>
    </tr>
  </table>
</body>
</html>"""
