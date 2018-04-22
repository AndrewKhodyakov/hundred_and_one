"""
    Here usefull utils
"""
from decimal import Decimal
import datetime

def model_to_dict(model):
    """
    extract model to dict
    """
    out = dict()
    for key in model.__dict__:
        if key != '_sa_instance_state':
            out[key] = model.__dict__.get(key)
            if isinstance(model.__dict__.get(key), datetime.date):
                out[key] = model.__dict__.get(key).isoformat()
            if isinstance(model.__dict__.get(key), Decimal):
                out[key] = float(model.__dict__.get(key))
    return out
        
