import os
from flask import Flask, request
from flask import jsonify

app = Flask(__name__)

@app.route('/processManualUpload', methods=['POST'])
def processManualUpload():
	print('Received request for /processManualUpload')
	# Rest of your code...
	# print recived data
	print(request.json)
	return jsonify(message="Success")

if __name__ == '__main__':
	app.run(host='0.0.0.0', port=5000)
