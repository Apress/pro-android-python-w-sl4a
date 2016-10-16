import android, datetime, smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

droid = android.Android()

smtp_server = 'smtp.gmail.com'
smtp_port = 587
mailto = 'paul'
mailfrom = 'paul'
password = 'password'

# Build our SMTP compatible message
msg = MIMEMultipart()
msg['Subject'] = 'SMS Message Export'
msg['To'] = mailto
msg['From'] = mailfrom

# Walk throu the SMS messages and add them to the message body
SMSmsgs = droid.smsGetMessages(False).result

body = ''
for message in SMSmsgs:
  millis = int(message['date'])/1000
  strtime = datetime.datetime.fromtimestamp(millis)
  body += strtime.strftime("%m/%d/%y %H:%M:%S") + ',' + message['address'] + ',' + message['body'] + '\n'

msg.attach(MIMEText(body, 'plain'))
smtpObj = smtplib.SMTP(smtp_server,smtp_port)
smtpObj.starttls()
smtpObj.login(mailfrom,'dummy1')
smtpObj.sendmail(mailfrom,mailto,msg.as_string())
smtpObj.close()
