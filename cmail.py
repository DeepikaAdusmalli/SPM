import smtplib
from smtplib import SMTP
from email.message import EmailMessage
def sendmail(to,subject,body):
    server=smtplib.SMTP_SSL('smtp.gmail.com',465)
    server.login('deepthiadusumalli2003@gmail.com','xufshlwbmpmjoijr')
    msg=EmailMessage()
    msg['From']='lavanyaadusumalli2003@gmail.com'
    msg['Subject']=subject
    msg['To']=to
    msg.set_content(body)
    server.send_message(msg)
    server.quit()
