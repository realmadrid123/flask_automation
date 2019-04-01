from flask import Flask, render_template, request, flash, redirect, url_for, session, logging
import json
import pyrebase
import RPi.GPIO as GPIO
import time
import signal
import sys

welcome = Flask(__name__)

welcome.secret_key = "home automation system"
config = {
    'apiKey': "AIzaSyBtQ3RAYAwHmXlLf5SUkXUOPfKUt-0jgOs",
    'authDomain': "iothome-6bab7.firebaseapp.com",
    'databaseURL': "https://iothome-6bab7.firebaseio.com",
    'projectId': "iothome-6bab7",
    'storageBucket': "iothome-6bab7.appspot.com",
    'messagingSenderId': "191054227706"
}

pyre_base = pyrebase.initialize_app(config)

auth = pyre_base.auth()

database = pyre_base.database()
# python_firebase = firebase.FirebaseApplication(config["https://iothome-6bab7.firebaseio.com"], None)

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# define sensors GPIOs
button = 20
senPIR = 16
pinTrigger = 18
pinEcho = 24

# define actuators GPIOs
ledRed = 17
ledYlw = 19
ledGrn = 26

# initialize GPIO status variables
buttonSts = 0
senPIRSts = 0
ledRedSts = 0
ledYlwSts = 0
ledGrnSts = 0

# Define button and PIR sensor pins as an input
GPIO.setup(button, GPIO.IN)
GPIO.setup(senPIR, GPIO.IN)

# Define led pins as output
GPIO.setup(ledRed, GPIO.OUT)
GPIO.setup(ledYlw, GPIO.OUT)
GPIO.setup(ledGrn, GPIO.OUT)

# turn leds OFF
GPIO.output(ledRed, GPIO.LOW)
GPIO.output(ledYlw, GPIO.LOW)
GPIO.output(ledGrn, GPIO.LOW)


# The function below is executed when someone requests a URL with the actuator name and action in it:
@welcome.route("/index")
def index():
    # Read GPIO Status
    buttonSts = GPIO.input(button)
    senPIRSts = GPIO.input(senPIR)
    ledRedSts = GPIO.input(ledRed)
    ledYlwSts = GPIO.input(ledYlw)
    ledGrnSts = GPIO.input(ledGrn)

    templateData = {
        'button': buttonSts,
        'senPIR': senPIRSts,
        'ledRed': ledRedSts,
        'ledYlw': ledYlwSts,
        'ledGrn': ledGrnSts,
    }
    return render_template('index.html', **templateData)


@welcome.route("/<deviceName>/<action>")
def action(deviceName, action):
    if deviceName == 'ledRed':
        actuator = ledRed
    if deviceName == 'ledYlw':
        actuator = ledYlw
    if deviceName == 'ledGrn':
        actuator = ledGrn

    if action == "on":
        GPIO.output(actuator, GPIO.HIGH)
    if action == "off":
        GPIO.output(actuator, GPIO.LOW)

    database.child("device").set({deviceName:action})
    buttonSts = GPIO.input(button)
    senPIRSts = GPIO.input(senPIR)
    ledRedSts = GPIO.input(ledRed)
    ledYlwSts = GPIO.input(ledYlw)
    ledGrnSts = GPIO.input(ledGrn)

    templateData = {
        'button': buttonSts,
        'senPIR': senPIRSts,
        'ledRed': ledRedSts,
        'ledYlw': ledYlwSts,
        'ledGrn': ledGrnSts,
    }
    return render_template('index.html', **templateData)


@welcome.route('/')
def landing_page():
    return render_template('home.html')


@welcome.route('/about')
def about():
    return render_template('about.html')


@welcome.route('/register', methods=['GET', 'POST'])
def registration():
    errorMessage = ''
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        mobile = request.form['mobile']
        address = request.form['address']
        try:
            user = auth.create_user_with_email_and_password(email, password)
            uid = user['localId']
            print(uid)
            data = {"name": name, "status": "1", 'email': email, 'mobile': mobile, "address":address}
            database.child("member").child(uid).child("details").set(data)
            return redirect(url_for('login_page', r="done"))
        except Exception as e:
            if len(password) < 6:
                errorMessage = 'Password must be at least 6 characters'
            else:
                errorMessage = 'An account with that email already exists'
    return render_template('register.html', errorMessage=errorMessage, user=None)


@welcome.route('/login', methods=['GET', 'POST'])
def login_page():
    errorMessage = ''
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        try:
            user = auth.sign_in_with_email_and_password(email, password)
            #print(auth.get_account_info(user['idToken']))
            print(user)
            session['uid'] = user['localId']
            return redirect(url_for('landing_page'))
        except Exception as e:
            errorMessage = e
    # if request.method =="GET" and request.args.get('r')=='done':
    return render_template('login.html', errorMessage=errorMessage)


@welcome.route('/logout')
def logout():
    session.pop('uid', None)
    return redirect(url_for('landing_page'))


@welcome.route('/reset-password', methods=['GET', 'POST'])
def  reset_password():
    errorMessage = ''
    if request.method == 'POST':
        email = request.form['email']
        try:
            auth.send_password_reset_email(email)
            return render_template('display-message.html', message='A password reset email will be sent to you shortly.')
        except:
            errorMessage = 'Invalid email'
    return render_template('reset-password.html', errorMessage=errorMessage, user=None)


if __name__ == "__main__":
    welcome.run(debug=True)
