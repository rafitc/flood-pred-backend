
from crypt import methods
from operator import methodcaller
from flask import Flask, render_template, request
import os
from werkzeug.utils import secure_filename
import json
import pandas as pd
import numpy as np
from keras.models import model_from_json
import datetime

app = Flask(__name__)

json_file = open('CNNmodel.json', 'r')
loaded_model_json = json_file.read()
json_file.close()
loaded_model = model_from_json(loaded_model_json)
loaded_model.load_weights("CNNmodel.h5") 
print("Loaded model from disk")  
loaded_model.summary()

database_url = "https://rain-pred-default-rtdb.firebaseio.com"

import firebase_admin
from firebase_admin import credentials, db

cred = credentials.Certificate("rain-pred-firebase-adminsdk-25cmt-bcadd39ba6.json")
firebase_admin.initialize_app(cred, {
	'databaseURL':database_url
})



@app.route('/')
def hello_world():
	return 'Hello World'

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
#	print(data)
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
	print("Dome")
	return jsonStr


if __name__ == '__main__':
	app.run(port=600, host="0.0.0.0", debug=True)