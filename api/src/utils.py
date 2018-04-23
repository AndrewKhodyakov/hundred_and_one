"""
    Here usefull utils
"""
from decimal import Decimal
import datetime
import logging
from sqlalchemy import (Table, Column, Numeric, Integer, String, \
    DateTime, MetaData, ForeignKey)
from sqlalchemy_utils import database_exists, create_database

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
        
def check_datebase_initialization(engine, log_level):
    """
    check is database is exists if not - create it
    engine: data base connacions engine
    log_level: logs level
    """
    logging.basicConfig(
        format=\
            '%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S', level=log_level)
    logger = logging.getLogger('Db initializer')

    logger.info('Check database...')
    if not database_exists(engine.url):
        logger.info('Db {} is not exists - start create it ...'.format(engine.url))
        
        create_database(engine.url)
        metadata = MetaData()
        one_hundred_report_table = Table('one_hundred_report', metadata,
            Column('P_K', Integer, primary_key=True),
            Column('REGN', Integer),
            Column('PLAN', String(length=1)),
            Column('NUM_SC', String(length=10)),
            Column('A_P', String(length=1)),
            Column('VR', Numeric),
            Column('VV', Numeric),
            Column('VITG', Numeric),
            Column('ORA', Numeric),
            Column('OVA', Numeric),
            Column('OITGA', Numeric),
            Column('ORP', Numeric),
            Column('OVP', Numeric),
            Column('OITGP', Numeric),
            Column('IR', Numeric),
            Column('IV', Numeric),
            Column('IITG', Integer),
            Column('DT', DateTime),
            Column('PRIZ', Integer),
        )
        metadata.create_all(engine)
