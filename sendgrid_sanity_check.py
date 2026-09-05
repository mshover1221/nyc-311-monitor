import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

message = Mail(
    from_email='noreply@nyc311alerts.com',
    to_emails='mshover9859@gmail.com',
    subject='Real Delivery Test',
    html_content='<strong>This is a real delivery test.</strong>'
)

try:
    sg = SendGridAPIClient(os.getenv("SENDGRID_API_KEY"))
    response = sg.send(message)
    print("STATUS:", response.status_code)
except Exception as e:
    print("ERROR:", e)

