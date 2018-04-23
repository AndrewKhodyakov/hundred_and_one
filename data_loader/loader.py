"""
    Data loader
"""
import os
from io import BytesIO
import unittest
import logging 
import time
import datetime
from itertools import count
import argparse
import zipfile
import rarfile
from dbfread import DBF
import requests
import responses

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import (Table, Column, Numeric, Integer, String, \
    DateTime, MetaData, ForeignKey)
from models import OneHundredReport

get_level = lambda: logging.DEBUG if os.environ.get('DEBUG') else logging.INFO
logging.basicConfig(
    format=\
        '%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S', level=get_level())

zero_number_strip = lambda data: data[1] if data[0] == '0' else data
add_zero_number = lambda data: '0' + data if int(data) < 10 else data

class Loader:
    """
    loader instance
    """
    def __init__(self):
        """
        do initialization and read ENVs
        """
        self._logger = logging.getLogger(__name__)
        self._period = dict()
        from_date = os.environ.get('FROM_DATE', '')
        to_date = os.environ.get('TO_DATE', '')

        self._base_url = os.environ.get('SOURSE_URL', '')
        self._db_url = os.environ.get('DB_URL', '')
        self._sessionmaker = None
        self._session = None
        self._tmp_folder = os.environ.get('TMP_FOLDER', '../tmp')
        self._dbf_files = []
        self._retry_timeout = int(os.environ.get('RETRY_TIMEOUT', '10'))
        self._complite = False

        #here check attributes
        if from_date and to_date:
            self._period['from'] = from_date
            self._period['to'] = to_date
            self._period['ranges'] = self._check_and_split_period()
        else:
            raise AttributeError('FROM_DATE or TO_DATE envs are not defined')

        if not self._base_url:
            raise AttributeError('SOURSE_URL env is not defined')

        if not self._db_url:
            raise AttributeError('DB_URL env is not defined')

        if not os.path.exists(self._tmp_folder):
            raise AttributeError('TMP_FOLDER - {}, is not existst'.format(self._tmp_folder))

        self._logger.info('Created : {}'.format(self))


    def _check_and_split_period(self):
        """
        validate datetime values and split period
        """
        out = []
        tmp = dict.fromkeys(self._period.keys())
        if len(set(self._period.values())) == 1:
            raise ValueError('Dates are should`t be equal {}'.format(self._period))

        for key in self._period.keys():
            date = self._period.get(key)
            if len(date) != 8:
                raise ValueError('Too small date value {}'.format(date))
            month = zero_number_strip(date[4:6])
            day = zero_number_strip(date[-2:])
            tmp[key] = datetime.date(year=int(date[:4]), month=int(month), day=int(day))

        if (tmp.get('to').month == tmp.get('from').month) and \
            (tmp.get('to').year == tmp.get('from').year):
            out.append(str(tmp.get('to').year) + add_zero_number(str(tmp.get('to').month)))

        else:
            delta = tmp['to'] - tmp['from']
            last = tmp['to']
            for day in range(1, delta.days + 1):
                _ = tmp['from'] + datetime.timedelta(hours=24*day)
                if _.month != last.month:
                    out.append(str(last.year) + add_zero_number(str(last.month)))
                    last = _
    
            self._logger.debug('Period splited at : {}'.format(out))
        return out

    @property
    def _db(self):
        """
        Create db connection
        """
        if not self._sessionmaker:
            self._sessionmaker = sessionmaker(bind=create_engine(self._db_url))
            self._session = self._sessionmaker()

        return self._session


    def run(self):
        """
        run loader
        """
        #if we has no data from this period do all actions
        if self._count() == 0:

            while not self._complite:
    
                try:
                    #try do all actions
                    self._load_data()
                    self._sent_data_to_db()
                    self._complite = True
    
                except ConnectionError as con_err:
                    #here we are if script can`t got responce
                    self._logger.error('Can`t complite cycle error: {}, station: {}'.\
                            format(con_err, self))
    
                self._logger.info('Whait {} sec, and try again...'.format(self._retry_timeout))
                time.sleep(self._retry_timeout)

    def _count(self):
        """
        Check is data for period is already exists in db
        """
        self._logger.info('Check data for period from {} to {} in db: {}'.\
            format(self._period.get('from'), self._period.get('to'), self._db_url))

        month = zero_number_strip(self._period.get('from')[4:6])
        day = zero_number_strip(self._period.get('from')[-2:])
        _from = datetime.date(\
            year=int(self._period.get('from')[:4]), month=int(month), day=int(day))

        month = zero_number_strip(self._period.get('to')[4:6])
        day = zero_number_strip(self._period.get('to')[-2:])
        _to = datetime.date(\
            year=int(self._period.get('to')[:4]), month=int(month), day=int(day))

        return self._db.query(OneHundredReport).filter(\
            OneHundredReport.DT>=_from, OneHundredReport.DT <=_to).count()

    @property
    def _urls(self):
        """
        Build urls
        """
        out = []
        for inst in self._period.get('ranges'):
            tmp = datetime.date(year=int(inst[:4]), \
                month=int(zero_number_strip(inst[-4:-2])),\
                    day=int(zero_number_strip(inst[-2:])))
            prefix = '01.rar'
            if tmp.year < 2009:
                prefix = '01.zip'
            out.append(self._base_url + '/101-' + inst + prefix)
        return out

    def _load_data(self):
        """
        load and store data in tmp volume
        """
        self._logger.info('{} - start load data from source... '.format(self))
        for url in self._urls:
            self._logger.debug('Try get data by url {}...'.format(url))

            resp = requests.get(url)

            #if server return not 200, we can`t work, check params
            if not resp.ok:
                raise ConnectionError(\
                    'Bad request params, check ENVs - loader {}, req - {}'.\
                        format(self, resp.text))

            #load data from server
            with open(os.path.join(self._tmp_folder, url.split('/')[-1:][0]), 'wb') as output:
                for chank in resp:
                    output.write(chank)
                self._logger.info('File {}, was successfull saved'.format(output))


    def _decompress_data(self):
        """
        decompress data
        """
        self._logger.info('Start decomress files {} ...'.format(os.listdir(self._tmp_folder)))
        tmp = [f_name for f_name in  os.listdir(self._tmp_folder) \
            if 'zip' in f_name or 'rar' in f_name]
        for arch_path in tmp:
            arch_driver = None

            #choose archivator
            if 'rar' in arch_path:
                arch_driver = rarfile.RarFile

            elif 'zip' in arch_path:
                arch_driver = zipfile.ZipFile

            #extract file from archive
            with arch_driver(self._tmp_folder + '/' + arch_path) as archive:
                for f_name in archive.namelist():
                    if 'B1.DBF' in f_name:
                        archive.extract(f_name, path=self._tmp_folder)
                        self._dbf_files.append(f_name)
                        self._logger.info('File {} was extracted...'.format(f_name))

            #delete usless archive
            self._logger.debug('Delete usless archive {}...'.format(arch_path))
            os.remove(self._tmp_folder + '/' + arch_path)



    def _sent_data_to_db(self):
        """
        create instance and store at database
        """
        for path_to_dbf in self._dbf_files:
            with DBF(self._tmp_folder + '/' + path_to_dbf, encoding='cp866') as table:
                counter = count()
                tmp = []
                for data in table:
                    data = dict(data)
                    #save only data with REGN and DT
                    if data.get('REGN') and data.get('DT'):
                        tmp.append(OneHundredReport(**data))
                        if next(counter) == 1000:
                            self._db.bulk_save_objects(tmp)
                            counter = count()
                            tmp = []

                if tmp:
                    self._db.bulk_save_objects(tmp)
                        

    def __repr__(self):
        """
        pretty print
        """
        return "\n\tLoader |url {}|db {}|folder {}|timeout {}|period {}, {}"\
            .format(self._base_url, self._db_url, self._tmp_folder, \
                self._retry_timeout, self._period.get('from'), self._period.get('to'))

class TestInstances(unittest.TestCase):
    """
    test file instances
    """
    def setUp(self):
        """
        set up test case
        """
        os.environ['SOURSE_URL'] = 'http://test_source.com/credit/forms'
        os.environ['DB_URL'] = 'sqlite://'
        os.environ['TMP_FOLDER'] = '../tmp'
        os.environ['RETRY_TIMEOUT'] = '2'
        self.rar_bytes_stream = BytesIO(\
b'Rar!\x1a\x07\x00\xcf\x90s\x00\x00\r\x00\x00\x00\x00\x00\x00\x00z\xadt \x901\x00G\x01\x00\x00\xe8\x03\x00\x00\x03l\x98zkU\x9b\x94L\x1d3\x0f\x00\xb4\x81\x00\x00test\\testB1.DBF\x00\xc0\t\xddQM\x0b\xd5\x80\xd7\xbd\xd5\xd4G\xe0\rh\x8d1\x97"vv3V\x03LX\x9a@Y\xb0\x8ce\r:\x0f\x81\xa2\xda\x82\x8bZ\xa0\xd4\xd6\xd0\xb546>\x02\xef\x81#S/H#c\xe0*L\xce\xe8\xb2+\x1d7Az\xc0Q\x1b2\xbc9\x99\xcc\xe79\x9e?\xc3\xa7s\xe0\x19G\xe3\xfes\xa7L\x0c\xc3\xfex\x15\xd5\xf5<]\xfd\xbaD\xd5\xa5\x88RPS\xf9\xf5]\'\x8fg\xc0n\xc9v\x90\xefh4\x05\xe4Em\xa83\x82&_wOF\xbe\x94\xb2^\xdd\x98\xd1\xeaa\x96\xab\xbcM\x8d\xe8\xcb\xd2\xa9(\xb5\x0b\xf2\x97G\x02\x0f\x0e\xfe\xeb]a\x0e\xa1\x033\x93\xac\xaa\xdbHv\xe4\x15I\xb9\x18^2L\x95\x9fh\x9c\xfc\xb3|\x80\xb5\xa1A\xc2My\x19\x05\x9c\xcd\x0c\x17\xf7\x7f\x03\x0e"\xf5*,\x82\x0b\x1e\xbf\xb2\x8ef\x0cB\xeeO\x0bwX\x05\x8c(\xe0\xd6?\x18\x16,\xab\x83/\xfd\xbf2\xe0\x8d\xc1d\xe6\xcd\xb4\xd3a/G/>\xe6\xa18\x80-\xb4\x93\xf6\xc1"\x93\xd2\xdbH\x0el\xa3\xa8?:\xe6\xa9\x92\xbb\x19j\x06\r\xf3\xb1<\xec\x83"\xbf\r\x89\xdf\xf4\x0f\xfe\xca\x7ffx\xe6[\xccbE\xaeC\xb5=\x18\xdc\xca;2\xd9\xd8\xfd\'W3\xa8\x1b\x87\xfb&\xfc\x90\xc4={\x00@\x07\x00'
        )


    def test_instance_creation(self):
        """
        create instance test, check periods validations
        """
        os.environ['FROM_DATE'] = '20081110'
        os.environ['TO_DATE'] = '20090305'
        loader = Loader()
        tmp  = {'from': '20081110', 'to': '20090305',\
            'ranges': ['200903', '200811', '200812', '200901', '200902']}
        self.assertDictEqual(tmp, loader._period)

    @responses.activate
    def test_do_request_and_load_data(self):
        """
        test for requests executing, load and save data
        """
        os.environ['FROM_DATE'] = '20100501'
        os.environ['TO_DATE'] = '20100502'
        loader = Loader()
        responses.add(responses.GET, 'http://test_source.com/credit/forms/101-20100501.rar',\
            body=self.rar_bytes_stream.readline(), status=200, \
                content_type='application/x-zip-compressed', stream=True)
        loader._load_data()

    def test_decompress_data(self):
        """
        test for decompress data file from archive
        """
        os.environ['FROM_DATE'] = '20100501'
        os.environ['TO_DATE'] = '20100502'
        loader = Loader()
        with open(loader._tmp_folder + '/test_rar_archive.rar', 'wb') as rar_arch:
            for chank in self.rar_bytes_stream:
                rar_arch.write(chank)
        loader._decompress_data()
        self.assertTrue(os.path.exists(loader._tmp_folder + '/test/testB1.DBF'))

        for inst in os.listdir(loader._tmp_folder + '/test'):
            os.remove(loader._tmp_folder + '/test/' + inst)

    def test_read_dbf_and_store_to_db(self):
        """
        test read dbf and store data to db
        """
        #create instance and call _db method for create connection
        os.environ['FROM_DATE'] = '20100501'
        os.environ['TO_DATE'] = '20100502'
        loader = Loader()
        loader._db

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
        metadata.create_all(loader._sessionmaker.__dict__.get('kw').get('bind'))

        #test read dbm file and save data in database
        with open(loader._tmp_folder + '/test_rar_archive.rar', 'wb') as rar_arch:
            for chank in self.rar_bytes_stream:
                rar_arch.write(chank)
        loader._decompress_data()
        loader._sent_data_to_db()
        self.assertTrue(loader._count() != 0)


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('mode', \
        help='Set mode "tests" - to run unittests or "run" for start loading.\n' + \
            'NOTE: for successfull running you should export all requred ENVs: \n' + \
            '\t FROM_DATE, TO_DATE, TMP_FOLDER, SOURSE_URL, DB_URL',\
            default='')

    args = parser.parse_args()
    #unittests mode
    if args.mode == 'tests':
        suite = unittest.TestSuite()
        suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TestInstances))
        unittest.TextTestRunner().run(suite)

    #run mode
    elif args.mode == 'run':
        loader = Loader()
        loader.run()

    #print help
    else:
        parser.print_help()
