"""
    Here usefull utils
"""
import os
from decimal import Decimal
import datetime
import logging
from sqlalchemy import create_engine
from sqlalchemy import (Table, Column, Integer, BigInteger, String, \
    DateTime, MetaData, ForeignKey)
from sqlalchemy_utils import database_exists, create_database, drop_database

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
        
def check_datebase_initialization():
    """
    check is database is exists if not - create it
    """
    engine = create_engine(os.environ.get('DB_URL', 'sqlite:///:memory:'))
    LOG_LEVEL = logging.DEBUG if os.environ.get('DEBUG')\
        else logging.INFO
    logging.basicConfig(
        format=\
            '%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S', level=LOG_LEVEL)
    logger = logging.getLogger('Db initializer')

    if os.environ.get('DROP_DB'):
        logger.info('Drop DB ENV detected, drop db...')
        drop_database(engine.url)

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
            Column('VR', BigInteger),
            Column('VV', BigInteger),
            Column('VITG', BigInteger),
            Column('ORA', BigInteger),
            Column('OVA', BigInteger),
            Column('OITGA', BigInteger),
            Column('ORP', BigInteger),
            Column('OVP', BigInteger),
            Column('OITGP', BigInteger),
            Column('IR', BigInteger),
            Column('IV', BigInteger),
            Column('IITG', BigInteger),
            Column('DT', DateTime),
            Column('PRIZ', Integer),
        )
        metadata.create_all(engine)
