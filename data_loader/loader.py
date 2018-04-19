"""
    Data loader
"""
import os
import unittest
import logging 
import time
import datetime
import requests

get_level = lambda: logging.DEBUG if os.environ.get('DEBUG') else logging.INFO
logging.basicConfig(
    format=\
        '%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S', level=get_level())

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
        self._db = None
        self._tmp_folder = os.environ.get('TMP_FOLDER', '../tmp')
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
            month = date[4:6]
            if month[0] == '0':
                month = month[1]
            day = date[-2:]

            if day[0] == '0':
                day = day[1]

            tmp[key] = datetime.date(year=int(date[:4]), month=int(month), day=int(day))

        delta = tmp['to'] - tmp['from']
        last = tmp['to']

        for day in range(1, delta.days + 1):
            _ = tmp['from'] + datetime.timedelta(hours=24*day)
            if _.month != last.month:
                month = str(last.month)
                if last.month < 10:
                    month = '0' + str(last.month)
                out.append(str(last.year) + month)
                last = _

        self._logger.debug('Period splited at : {}'.format(out))
        return out

    def run(self):
        """
        run loader
        """
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

    def _get_db_connect(self):
        """
        Create db connection
        """
        self._logger.info('{} - try to create connection to db... '.format(self))

    @property
    def _urls(self):
        """
        Build urls
        """
        out = []
        for inst in self._period.get('ranges'):
            tmp = datetime.date(year=inst[:4])
            prefix = '01.rar'
            if tmp.year < 2009:
                prefix = '01.zip'
            out.append(self._base_url + '/' + inst + prefix)
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

            with open(url.split('/')[-1:][0], 'wb') as output:
                for chank in resp:
                    output.write(chank)
                self._logger.info('File {}, was successfull saved'.format(output))

    def _sent_data_to_db(self):
        """
        decompess and create instances
        """
        self._get_db_connect()
        #TODO decompress data
        #TODO create models and save they

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
        os.environ['SOURSE_URL'] = 'http://test_source.com'
        os.environ['DB_URL'] = 'sqlite://'
        os.environ['TMP_FOLDER'] = '../tmp'
        os.environ['RETRY_TIMEOUT'] = '2'

    def test_instance_creation(self):
        """
        """
        os.environ['FROM_DATE'] = '20081110'
        os.environ['TO_DATE'] = '20090305'
        loader = Loader()
        tmp  = {'from': '20081110', 'to': '20090305',\
            'ranges': ['200903', '200811', '200812', '200901', '200902']}
        self.assertDictEqual(tmp, loader._period)

    def test_do_request_and_load_data(self):
        """
        """
        pass

if __name__ == "__main__":
    unittest.main()
