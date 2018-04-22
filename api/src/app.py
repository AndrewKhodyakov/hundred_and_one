"""
    Here application
"""
from flask import Flask
from flask import jsonify
from flask import abort
from settings import (LOG_LEVEL, DB)
from models import OneHundredReport
from utils import model_to_dict

app = Flask(__name__)
app.logger.setLevel(LOG_LEVEL)
setattr(app, 'db', DB)

@app.route('/one_hundred_report/<int:regn>')
def one_hundred_report(regn):
    """
    Get data about organization one_hundred_report through it REGN
    """
    return jsonify([model_to_dict(inst) for inst in \
        app.db.query(OneHundredReport).filter(OneHundredReport.REGN == regn)])
