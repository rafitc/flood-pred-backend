
#from crypt import methods
from crypt import methods
from operator import methodcaller
from flask import Flask, jsonify, render_template, request
import os
from matplotlib.pyplot import prism
from werkzeug.utils import secure_filename
import json
import pandas as pd
import numpy as np
from keras.models import model_from_json
import datetime
from flask_cors import CORS
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from twilio.rest import Client

app = Flask(__name__)
CORS(app)
# json_file = open('CNNmodel.json', 'r')
# loaded_model_json = json_file.read()
# json_file.close()
# loaded_model = model_from_json(loaded_model_json)
# loaded_model.load_weights("CNNmodel.h5") 
# print("Loaded model from disk")  
# loaded_model.summary()

# Your Account SID from twilio.com/console
account_sid = "AC6f9f263116ddd31b1c300a9519fd7530"
# Your Auth Token from twilio.com/console
auth_token  = "7d8272b867f0e9d78e57852978892b90"

database_url = "https://rain-pred-default-rtdb.firebaseio.com"

import firebase_admin
from firebase_admin import credentials, db

cred = credentials.Certificate("rain-pred-firebase-adminsdk-25cmt-bcadd39ba6.json")
firebase_admin.initialize_app(cred, {
	'databaseURL':database_url
})

kerala_dist = ["Nothing","Kasaragod","Kannur","Wayanad","Kozhikode","Malappuram","Palakkad","Thrissur","Ernakulam","Idukki","Kottayam","Alappuzha","Pathanamthitta","Kollam","Thiruvananthapuram"]


def send_sms(toNumber, content):
	client = Client(account_sid, auth_token)
	message = client.messages.create(
    	to=toNumber, 
    	from_="+19897472583",
    	body=content)
	return(message.sid)

@app.route('/')
def hello_world():
	return render_template('index.html')


@app.route('/test_api',methods=['GET','POST'])            
def test_api():
    uploaded_file = request.files['document']
    data = json.load(request.files['data'])
    filename = secure_filename(uploaded_file.filename)
    uploaded_file.save(os.path.join('/Users/rafi/Desktop/rainPrediction/backend/flask-backend/files', filename))
    print(data)
    return 'success'

@app.route('/admin',methods=['GET','POST'])            
def admin():
	return render_template('file.html')

@app.route("/predict", methods=['GET', 'POST'])
def predict():
	# uploaded_file = request.files['document']
	# data = json.load(request.files['data'])
	# filename = secure_filename(uploaded_file.filename)
	# uploaded_file.save(os.path.join('/Users/rafi/Desktop/rainPrediction/backend/flask-backend/files', filename))
	# print(data)
	li = []
	predicted_value = []
	today = datetime.datetime.now()
	today = str(today.year)+str(today.month)+str(today.day)
	#read and parse json 
	with open('files/test.json', 'r') as fp:
		data = json.load(fp)
	for key in data:
		value = data[key]
		for i in value:
			li.append(value[i])
		#print(li)
		x_test = li
		x_test  = pd.DataFrame(x_test)

		x_test = np.stack([x_test, x_test], axis=0)
		#print(x_test.T.shape,x_test.T)
		y_pred = loaded_model.predict(x_test.T)[:,0]

		pred = np.empty((1,len(y_pred)), dtype=object)
		pred = np.where(y_pred>=0.47, 1, 0)
		y_train = np.reshape(y_pred,len(y_pred))
		pred = np.reshape(pred,len(pred))
		li = []
		predicted_value.append(pred.item(0))
		#print("pred of ", key," is ", pred)
	x = {
        "1": predicted_value[0],
        "2": predicted_value[1],
        "3": predicted_value[2],
        "4": predicted_value[3],
        "5": predicted_value[4],
        "6": predicted_value[5],
        "7": predicted_value[6],
        "8": predicted_value[7],
        "9": predicted_value[8],
        "10": predicted_value[9],
        "11": predicted_value[10],
        "12": predicted_value[11],
        "13": predicted_value[12],
        "14": predicted_value[13],
    }
	jsonStr = json.dumps(x)
	#check the date 
	ref = db.reference("/predicted")
	ref.set(jsonStr)
	print("Done")
	return jsonStr

@app.route('/getvalue', methods=["GET"])
def getValue():
	ref = db.reference("/")
	j_value = ref.get()
	k = j_value['predicted']
	k = json.loads(k)
	print(k)
	return jsonify(k)

@app.route("/formotp", methods=["GET"])
def form():
	return render_template('otp.html')

from itsdangerous import URLSafeTimedSerializer
import time
def generate_confirmation_token(email):
    serializer = URLSafeTimedSerializer("12ewewjindcdsk")
    return serializer.dumps(email, salt="qwertyui")


def confirm_token(token, expiration=3600):
    serializer = URLSafeTimedSerializer("12ewewjindcdsk")
    try:
        email = serializer.loads(
            token,
            salt="qwertyui",
            max_age=expiration
        )
    except:
        return "Time Expired "
    return email

@app.route("/otp", methods=["GET"])
def otp():
	a = generate_confirmation_token("9747165032")
	print(a)
	time.sleep(2)
	return(confirm_token(a, 3600))

@app.route('/value', methods=["POST"])
def storeValue():
	name = request.form.get("name")
	pin = request.form.get("pin")
	mobile = request.form.get("mobile")
	if name == "" or name == " ":
		return "cant find name field"
	if pin == "" or pin == " ":
		return "cant find Pin code"
	if mobile == "" or mobile == " ":
		return "cant find mobile number"
	#pin code test
	# value = requests.get("")
	session = requests.Session()
	retry = Retry(connect=3, backoff_factor=0.5)
	adapter = HTTPAdapter(max_retries=retry)
	session.mount('http://', adapter)
	session.mount('https://', adapter)
	URL = "https://api.postalpincode.in/pincode/"+ pin
	value = session.get(URL)
	#print(value.content)
	my_json = value.content.decode('UTF-8')
	my_json = my_json[1:-1]
	my_json = json.loads(my_json)
	try:
		state = my_json.get("PostOffice")[0]
	except Exception as e:
		return("invalid pincode")
	state = state.get("State")
	print(state)
	a = 0
	if state == "Kerala":
		dist = (my_json.get("PostOffice")[0]).get("District")
		a = kerala_dist.index(dist)
		print(a)
	else:
		return "Not in kerala"

	ref = db.reference("/")
	ref.push({
    "user": {
            "name": name,
            "pin": pin,
			"dist": a,
            "mobile": mobile,
			"otp": False,
  }
})
	otp_token = generate_confirmation_token(mobile)
	sms = "click here to verify your mobile number with in 1Hr. http://localhost:600/token?key="+otp_token
	print(sms)
	#send sms 

	return "An OTP send to your Mobile Number. Click that to verify your Mobile Number | " + sms 

def updateEntryinOTP(mobileNumber):
	ref = db.reference("/")
	j_value = ref.get()
	for key in j_value:
		mobile = j_value.get(key).get('user').get('mobile')
		print(mobile)
		if mobile == mobileNumber:
			print("found match")
			name = j_value.get(key).get('user').get('name')
			pin = j_value.get(key).get('user').get('pin')
			a = j_value.get(key).get('user').get('dist')
			ref.child(key).update({
				"user": {
            		"name": name,
            		"pin": pin,
					"dist": a,
         			"mobile": mobile,
					"otp": True,
  }})
			return "You are succesfully authenticated your Mobile number"
	else:
		return "Something went wrong"
	
@app.route('/token/', methods=["GET"])
def verify():
	key = request.args.get('key')
	print(key)
	try:
		mob = confirm_token(key)
	except:
		return('The confirmation link is invalid or has expired.', 'danger')
	print("mob : ", mob)
	return(updateEntryinOTP(mob))

@app.route('/file', methods=["POST"])
def getfile():
	f = request.files['file'] 
	f.save(f.filename)  
	return "done"

@app.route('/sms', methods=["GET"])
def sendsms11():
	return(send_sms("+919747165032", "click here to verify your mobile number with in 1Hr. http://localhost:600/token?key="))


if __name__ == '__main__':
	app.run(port=600, host="0.0.0.0", debug=True)