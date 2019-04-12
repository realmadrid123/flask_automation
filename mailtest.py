import RPi.GPIO as gpio
import picamera
import time
import pyrebase

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from email.mime.image import MIMEImage
from flask import session

config = {
    'apiKey': "AIzaSyBtQ3RAYAwHmXlLf5SUkXUOPfKUt-0jgOs",
    'authDomain': "iothome-6bab7.firebaseapp.com",
    'databaseURL': "https://iothome-6bab7.firebaseio.com",
    'projectId': "iothome-6bab7",
    'storageBucket': "iothome-6bab7.appspot.com",
    'messagingSenderId': "191054227706"
}


data=""

def sendMail(data):
    fromaddr = "picameratest123@gmail.com"    # change the email address accordingly
    toaddr = "askuptech@gmail.com"
    mail = MIMEMultipart()
    mail['From'] = fromaddr
    mail['To'] = toaddr
    mail['Subject'] = "Attachment"
    body = "Please find the attachment"
    mail.attach(MIMEText(body, 'plain'))
    print(data)
    dat='%s.jpg'%data
    print(dat)
    attachment = open(dat, 'rb')
    image=MIMEImage(attachment.read())
    attachment.close()
    mail.attach(image)
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(fromaddr, "picameratest321")
    text = mail.as_string()
    server.sendmail(fromaddr, toaddr, text)
    server.quit()

def capture_image(uid):
    camera = picamera.PiCamera()
    camera.rotation=180
    camera.awb_mode= 'auto'
    camera.brightness=55
    data= time.strftime("%d_%b_%Y|%H:%M:%S")
    camera.start_preview()
    time.sleep(5)
    camera.capture('%s.jpg'%data)
    camera.stop_preview()
    time.sleep(1)
    print('data',data)
    sendMail(data)
    upload(uid,data)
    
    
def upload(uid,imagepath):
    print('uploading...')
    pyre_base = pyrebase.initialize_app(config)
    storage = pyre_base.storage()
    imagename=imagepath+".jpg"
    print('userid',uid)
    x=storage.child(f"images/{uid}/{imagename}").put(imagename,uid)
    print(x)



