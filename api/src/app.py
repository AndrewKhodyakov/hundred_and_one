"""
    Here application
"""
from flask import Flask
from flask import jsonify
from flask import abort
from settings import (LOG_LEVEL, DB)

app = Flask(__name__)
app.logger.setLevel(LOG_LEVEL)
setattr(app, 'db', DB)

@app.route('/one_hundred_report')
def one_hundred_report():
    payload = {"here": "will be data"}
    return jsonify(payload)
