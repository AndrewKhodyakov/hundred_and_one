import os
import logging
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

        self._logger.info('Created : {}'.foramt(self))


    def _check_and_split_period(self):
        """
        validate datetime values and split period
        """
        out = []
        tmp = dict.fromkeys(self._period.keys())
        if len(set(self._period.values())) == 1:
            raise ValueError('Dates are should`t be equal {}'.foramt(self._period))

        for key in self._period.keys():
            data = self._period.get(key)
            if len(date) != 8:
                raise ValueError('Too small date value {}'.foramt(date))
            month = date[4:6]
            if month[0] == '0':
                month = month[1]
            
            day = date[-2:]
            if day[0] == '0':
                day = day[1]
            
            tmp[key] = datetime.date(year=date[:4], month=month, day=day)

        delta = tmp['to'] - tmp['from']
        last = tmp['from']
        for day in range(1, delta.days + 1):
            _ = tmp['from'] + datetime.datetime(day=day)
            if _.month != last.month:
                month = last.month
                if last.month < 10:
                    month = '0' + str(last.month)
                out.append(str(last.year) + month)
                last = _

        self._logger.debug('Perod splited at : {}'.foramt(out))
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
                self._logger.error('Can`t complite cycle error: {}, station: {}'.\
                        format(con_err, self))

            self._logger.info('Whait {} sec, and try again...'.foramt(self._retry_timeout))
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
            self._logger.debug('Try get data by {}...'.format(url))

            resp = requests.get(url)

            #if server return not 200, we should check params
            if not resp.ok:
                raise ConnectionError(\
                    'Bad request params, check ENVs - loader {}, req - {}'.\
                        format(self, resp.text))

            with open(url.split('/')[-1:][0], 'wb') as output:
                for chank in resp:
                    output.write(chank)
                self._logger.debug('File {}, whas succesful saved'.format(output))

    def _sent_data_to_db:
        """
        """
        pass

    def __repr__(self):
        """
        pretty print
        """
        return "\n\tLoader ::url {}::db ::folder {}::timeout {}::period {}, {}"\
            .format(self._base_url, self._db_url, self._tmp_folder, \
                self._retry_timeout, self._period.get('from'), self._period.get('to'))


if __name__ == "__main__":
    pass
