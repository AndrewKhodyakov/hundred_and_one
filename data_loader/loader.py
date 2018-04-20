"""
    Data loader
"""
import os
import unittest
import logging 
import time
import datetime
import requests
import responses

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
            print(inst)
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
        os.environ['SOURSE_URL'] = 'http://test_source.com/credit/forms'
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

    @responses.activate
    def test_do_request_and_load_data(self):
        """
        """
        os.environ['FROM_DATE'] = '20081110'
        os.environ['TO_DATE'] = '20081111'
        loader = Loader()
        responses.add(responses.GET, 'http://test_source.com/credit/forms/101-20081101.zip',\
            body=b'asdfasdfasdfasddfasdf', status=200, \
                content_type='application/x-zip-compressed', stream=True)
        loader._load_data()

if __name__ == "__main__":
    unittest.main()
