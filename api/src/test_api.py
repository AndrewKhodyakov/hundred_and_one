import os
import json
import logging
import unittest
from sqlalchemy import (Table, Column, Numeric, Integer, String, DateTime, MetaData, ForeignKey)
from settings import ENGINE
from app import app

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
        metadata.create_all(ENGINE)

        self._data = {'REGN': 1, 'PLAN': 'А', 'NUM_SC': '10207', 'A_P': '2',\
            'VR': 23064358, 'VV': 0, 'VITG': 23064358.0, 'ORA': 0, 'OVA': 0, 'OITGA': 0.0,\
            'ORP': 0, 'OVP': 0, 'OITGP': 0.0, 'IR': 23064358, 'IV': 0, 'IITG': 23064358.0,\
            'DT': datetime.date(2010, 5, 1), 'PRIZ': 1}

    def test_a_models(self):
        """
        test OneHundredReport model
        """
        logging.info('\nStart model test..')

    def test_one_hundred_report_endpoint(self):
        """
        test for one_hundred_report
        """
        logging.info('\nStart endpoint test..')
        resp = json.loads(self._client.get('/one_hundred_report').\
            get_data().decode())
        print(resp)

if __name__ == "__main__":
    unittest.main()
