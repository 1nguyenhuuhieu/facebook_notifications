
import smtplib
from email.message import EmailMessage

sender_mail = "1nguyenhuuhieu@gmail.com"

password = "ycydocwufdfejphw"

reciever_mail = "huuhieung90@gmail.com"
 
# creates SMTP session
s = smtplib.SMTP('smtp.gmail.com', 587)
 
# start TLS for security
s.starttls()
 
# Authentication
s.login(sender_mail, password)
 
# message to be sent
msg = EmailMessage()
msg.set_content('This is my message')

msg['Subject'] = 'Subject'
msg['From'] = "1nguyenhuuhieu@gmail.com"
msg['To'] = "huuhieung90@gmail.com"
 
# sending the mail
s.send_message(msg)
 
# terminating the session
s.quit()
