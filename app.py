from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({"message": "Backend Flask hoạt động thành công!"})

from flask_cors import CORS

app = Flask(__name__)
CORS(app)
