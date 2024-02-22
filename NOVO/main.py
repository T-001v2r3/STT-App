import os
from flask import Flask, request
from flask_cors import CORS
from flask import jsonify

app = Flask(__name__)
CORS(app)

@app.route('/processManualUpload', methods=['POST'])
def processManualUpload():
	print('Received request for /processManualUpload')
	# Rest of your code...
	# print recived data
	print(request.json)
	return jsonify(message="Success")

def main():
	app.run(port=5000)

if __name__ == '__main__':
	main()
