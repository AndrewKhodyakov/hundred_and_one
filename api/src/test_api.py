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
            Column('p_k', Integer, primary_key=True),
            Column('regn', Integer),
            Column('plan', String(length=1)),
            Column('num_sc', String(length=10)),
            Column('a_p', String(length=1)),
            Column('vr', Numeric),
            Column('vv', Numeric),
            Column('vitg', Numeric),
            Column('ora', Numeric),
            Column('ova', Numeric),
            Column('oitga', Numeric),
            Column('orp', Numeric),
            Column('ir', Numeric),
            Column('iv', Numeric),
            Column('iitg', Integer),
            Column('dt', DateTime),
            Column('priz', Integer),
        )
        metadata.create_all(ENGINE)

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
