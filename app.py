
from crypt import methods
from operator import methodcaller
from flask import Flask, request
import os
from werkzeug.utils import secure_filename
import json
import pandas as pd
import numpy as np
from keras.models import model_from_json

app = Flask(__name__)

json_file = open('CNNmodel.json', 'r')
loaded_model_json = json_file.read()
json_file.close()
loaded_model = model_from_json(loaded_model_json)
loaded_model.load_weights("CNNmodel.h5") 
print("Loaded model from disk")  
loaded_model.summary()

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
	return "axmin"

@app.route("/predict", methods=['GET', 'POST'])
def predict():
	li = []
	#read and parse json 
	with open('test.json', 'r') as fp:
		data = json.load(fp)
	for key in data:
		value = data[key]
		for i in value:
			li.append(value[i])
		print(li)
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
		print("pred of ", key," is ", pred)
	return "done"


if __name__ == '__main__':
	app.run(port=600, host="0.0.0.0", debug=True)