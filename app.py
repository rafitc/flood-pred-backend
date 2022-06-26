#from crypt import methods
from crypt import methods
from operator import methodcaller
from flask import Flask, jsonify, render_template, request, flash 
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
json_file = open('CNNmodel.json', 'r')
loaded_model_json = json_file.read()
json_file.close()
loaded_model = model_from_json(loaded_model_json)
loaded_model.load_weights("CNNmodel.h5") 
print("Loaded model from disk")  
loaded_model.summary()

# Your Account SID from twilio.com/console
account_sid = ""
# Your Auth Token from twilio.com/console
auth_token  = ""

verified_mob_num = ""

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
	
	try:
		message = client.messages.create(
    	to=verified_mob_num, 
    	from_="+19897472583",
    	body=content)
		status = message.sid
	except:
		status = "error"
	return(status)

@app.route('/')
def hello_world():
	return render_template('index.html')


# @app.route('/test_api',methods=['GET','POST'])            
# def test_api():
#     uploaded_file = request.files['document']
#     data = json.load(request.files['data'])
#     filename = secure_filename(uploaded_file.filename)
#     uploaded_file.save(os.path.join('/Users/rafi/Desktop/rainPrediction/backend/flask-backend/files', filename))
#     print(data)
#     return 'success'

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
	jsonStr = json.loads(jsonStr)
	#check the date 
	ref = db.reference("/predicted")
	ref.set(jsonStr)
	print("Done")
	return jsonStr

from itsdangerous import URLSafeTimedSerializer
import time

def generate_confirmation_token(mobile):
    serializer = URLSafeTimedSerializer("12ewewjindcdsk")
    return serializer.dumps(mobile, salt="qwertyui")

def confirm_token(token, expiration=3600):
    serializer = URLSafeTimedSerializer("12ewewjindcdsk")
    try:
        mobile = serializer.loads(
            token,
            salt="qwertyui",
            max_age=expiration
        )
    except:
        return "Time Expired "
    return mobile

@app.route("/get_value", methods=["GET"])
def valueOfpred():
	ref = db.reference("/predicted")
	j_value = ref.get()
	print(j_value)
	x = {
        "1": j_value[1],
        "2": j_value[2],
        "3": j_value[3],
        "4": j_value[4],
        "5": j_value[5],
        "6": j_value[6],
        "7": j_value[7],
        "8": j_value[8],
        "9": j_value[9],
        "10": j_value[10],
        "11": j_value[11],
        "12": j_value[12],
        "13": j_value[13],
        "14": j_value[14],
    }
	print(type(x))
	return x


@app.route('/value', methods=["POST"])
def storeValue():
	name = request.form.get("name")
	pin = request.form.get("pin")
	mobile = request.form.get("mobile")
	print(name, " ",pin, mobile)
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
		return render_template("invalid_pin_code.html")

	ref = db.reference("/members")
	j_value = ref.get()
	if j_value == None:
		ref.push({
    	"user": {
            "name": name,
            "pin": pin,
			"dist": a,
            "mobile": mobile,
			"otp": False,
  		}})
	time.sleep(1)
	for key in j_value:
		Firebae_mobile = j_value.get(key).get('user').get('mobile')
		Firebae_verify = j_value.get(key).get('user').get('otp')
		if mobile == Firebae_mobile and Firebae_verify == True:
			return "Already registerd user"
		if mobile == Firebae_mobile and Firebae_verify == False:
			otp_token = generate_confirmation_token(mobile)
			sms = "click here to verify your mobile number with in 1Hr. http://localhost:600/token?key="+otp_token
			print(sms)
			#send sms 
			print(send_sms("+919747165032", sms))
			return sms 
			
	ref.push({
    "user": {
            "name": name,
            "pin": pin,
			"dist": a,
            "mobile": mobile,
			"otp": False,
  }})
	otp_token = generate_confirmation_token(mobile)
	sms = "click here to verify your mobile number with in 1Hr. http://localhost:600/token?key="+otp_token
	print(sms)
	#send sms 
	print(send_sms("+919747165032", sms))
	return render_template("check_mobile.html") 

def updateEntryinOTP(mobileNumber):
	ref = db.reference("/members")
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
			return render_template("mobile_verified.html")
	else:
		return "Something went wrong"
	
#To verify Mobile number 
@app.route('/token/', methods=["GET"])
def verify():
	key = request.args.get('key')
#	print(key)
	try:
		mob = confirm_token(key)
	except:
		return('The confirmation link is invalid or has expired.', 'danger')
	print("mob : ", mob)
	return(updateEntryinOTP(mob))

# @app.route('/file', methods=["POST"])
# def getfile():
# 	f = request.files['file'] 
# 	f.save(f.filename)  
# 	return "done"

# @app.route('/sendsms', methods=["GET"])
# def sendsms11():
# 	return(send_sms("+919747165032", "click here to verify your mobile number with in 1Hr. http://localhost:600/token?key="))

#To send SMS notification 
@app.route('/notify', methods=["GET"])
def notify():
	ref = db.reference("/predicted")
	get_json = ref.get()
	flood_dist = []
	#get flooded dist 
	count = -1
	for each in get_json:
		count += 1
		if count == 0:
			continue
		if 1 == int(each):
			flood_dist.append(count)
	print("Flood districts are : ")
	for x in flood_dist:
		print(kerala_dist[x])
	#sending sms 
	ref = db.reference("/members")
	j_value = ref.get()
	for key in j_value:
		name = j_value.get(key).get('user').get('name')
		dist = j_value.get(key).get('user').get('dist')
		mobile = j_value.get(key).get('user').get('mobile')
		verified = j_value.get(key).get('user').get('otp')
		if dist in flood_dist and verified == True:
			print("I'm sending alert to ", mobile)
			#send sms 
			sms = "Hello " + name +", There is a chance of flooding the next day in your district. Please take care."
			print(send_sms(mobile, sms))
			print(sms)
	return "Ok"
	
@app.route('/register', methods=["GET"])
def reguser():
	return render_template("register.html")

	
@app.route('/flash', methods=["GET"])
def fla():
	flash("hello")
	return render_template("register.html")

if __name__ == '__main__':
	app.run(port=600, host="0.0.0.0", debug=True) 
