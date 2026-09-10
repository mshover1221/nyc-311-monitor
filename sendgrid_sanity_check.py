import os
import sendgrid
from sendgrid.helpers.mail import Mail

api_key = os.getenv("SENDGRID_API_KEY")

if not api_key:
    raise RuntimeError("SENDGRID_API_KEY environment variable is not set")

sg = sendgrid.SendGridAPIClient(api_key=api_key)

message = Mail(
    from_email="alerts@nyc311alerts.com",
    to_emails="mshover985@gmail.com",
    subject="Test Alert",
    html_content="<strong>Hello from SendGrid!</strong>"
)

response = sg.send(message)

print(response.status_code)
print(response.body)
print(response.headers)
