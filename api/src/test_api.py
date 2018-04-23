import os
import json
import logging
import unittest
import datetime
from sqlalchemy import (Table, Column, Integer, BigInteger,
    String, DateTime, MetaData, ForeignKey)

from settings import ENGINE, DB
from app import app
from models import OneHundredReport
from utils import model_to_dict

get_level = lambda: logging.DEBUG if os.environ.get('DEBUG') else logging.INFO
logging.basicConfig(level=get_level())

class APITestCase(unittest.TestCase):
    """
    Main test case
    """
    def setUp(self):
        """
        crete app
        """
        #enable application test mode
        app.testing = True
        self._client = app.test_client()
        self.maxDiff = None

        #create test database in memory
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
        metadata.create_all(ENGINE)

        self._data = {'REGN': 1, 'PLAN': 'А', 'NUM_SC': '10207', 'A_P': '2',\
            'VR': 23064358, 'VV': 0, 'VITG': 23064358.0, 'ORA': 0, 'OVA': 0, 'OITGA': 0.0,\
            'ORP': 0, 'OVP': 0, 'OITGP': 0.0, 'IR': 23064358, 'IV': 0, 'IITG': 23064358.0,\
            'DT': datetime.date(2010, 5, 1), 'PRIZ': 1}

    def test_a_models_and_utils(self):
        """
        test OneHundredReport model
        """
        logging.info('\nStart model test..')
        inst = OneHundredReport(**self._data)
        DB.add(inst)
        res = DB.query(OneHundredReport).all()
        model = res.pop()
        self.assertEqual(str(model), '1_1_2010-05-01')
        self.assertDictEqual(model_to_dict(model), \
            {'REGN': 1, 'PLAN': 'А', 'NUM_SC': '10207', 'A_P': '2', 'VR': 23064358, 'VV':\
            0, 'VITG': 23064358.0, 'ORA': 0, 'OVA': 0, 'OITGA': 0.0, 'ORP': 0, 'OVP': 0,\
            'OITGP': 0.0, 'IR': 23064358, 'IV': 0, 'IITG': 23064358.0, 'DT':\
            '2010-05-01', 'PRIZ': 1, 'P_K':1})

        

    def test_one_hundred_report_endpoint(self):
        """
        test for one_hundred_report
        """
        logging.info('\nStart endpoint test..')
        DB.add(OneHundredReport(**self._data))
        resp = json.loads(self._client.get('/one_hundred_report/1').\
            get_data().decode())
        self.assertListEqual(
            [{'A_P': '2', 'DT': '2010-05-01T00:00:00', 'IITG': 23064358, 'IR':\
            23064358.0, 'IV': 0.0, 'NUM_SC': '10207', 'OITGA': 0.0, 'OITGP': 0.0, 'ORA':\
            0.0, 'ORP': 0.0, 'OVA': 0.0, 'OVP': 0.0, 'PLAN': 'А', 'PRIZ': 1, 'P_K': 1,\
            'REGN': 1, 'VITG': 23064358.0, 'VR': 23064358.0, 'VV': 0.0}, {'A_P': '2', 'DT':\
            '2010-05-01T00:00:00', 'IITG': 23064358, 'IR': 23064358.0, 'IV': 0.0, 'NUM_SC':\
            '10207', 'OITGA': 0.0, 'OITGP': 0.0, 'ORA': 0.0, 'ORP': 0.0, 'OVA': 0.0, 'OVP':\
            0.0, 'PLAN': 'А', 'PRIZ': 1, 'P_K': 2, 'REGN': 1, 'VITG': 23064358.0, 'VR':
            23064358.0, 'VV': 0.0}], resp)

if __name__ == "__main__":
    unittest.main()
