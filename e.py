import smtplib
from datetime import datetime
import pytz
# Import the email modules we'll need
from email.message import EmailMessage

# Open the plain text file whose name is in textfile for reading.
with open('/home/admin_/NBA-Machine-Learning-Sports-Betting/output.txt') as fp:
    # Create a text/plain message
    msg = EmailMessage()
    msg.set_content(fp.read())

# me == the sender's email address
# you == the recipient's email address
tz = pytz.timezone('America/New_York')
now_without_timezone = datetime.now().replace(tzinfo=pytz.utc)
now_with_timezone = now_without_timezone.astimezone(tz)
todays_date = now_with_timezone.strftime('%Y-%m-%d')
msg['Subject'] = f'NBA Forecasts for {todays_date}'
msg['From'] = 'tyroneschiff@gmail.com'
msg['To'] = 'tyroneschiff@gmail.com'

# Send the message via our own SMTP server.
with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
    smtp.login('tyroneschiff@gmail.com', 'sgvdrbslbmxcnmjo')
    smtp.send_message(msg)
    smtp.quit()