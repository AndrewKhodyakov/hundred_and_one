"""
    Here application
"""
from flask import Flask

app = Flask(__name__)

@app.route('/one_hundred_report')
def hello_world():
    return 'Here 101 '
