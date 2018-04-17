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

        #here check attributes
        if not from_date and not to_date:
            raise AttributeError('FROM_DATE and TO_DATE envs are not defined')
        else:
            for date in [from_date, to_date]:
                if len(date) != 8:
                    raise ValueError('Too small date value {}'.foramt(date))

                month = date[4:6]
                if month[0] == '0':
                    month = month[1]

                day = date[-2:]
                if day[0] == '0':
                    day = day[1]
                self._period[date] = datetime.date(year=date[:4], month=month, day=day)

        if not self._base_url:
            raise AttributeError('SOURSE_URL env is not defined')

        if not self._db_url:
            raise AttributeError('DB_URL env is not defined')

        if not os.path.exists(self._tmp_folder):
            raise AttributeError('TMP_FOLDER - {}, is not existst'.format(self._tmp_folder))

        self._logger.info('Created : {}'.foramt(self))

    def run(self):
        """
        run loader
        """
        pass

    def _get_db_connect(self):
        """
        Create db connection
        """
        self._logger.info('{} - try to create connection to db... '.format(self))

    @property
    def urls(self):
        """
        Build urls
        """
        out = None

#        if len(self._period) == 1:
#            out = [self._base_url + '/' + self._period.get(key)[:-2] + '01' \
#                for key in self._period.keys()]
#
#        else:
#            tmp = list(self._period.keys())
#            start = None
#            if self._period.get(tmp[0]) > self._period.get(tmp[1]):
#                start = tmp[0]
#            else:
#                start = tmp[1]
#
#        for url in out:
#            if 

        return out
            
    def _load_data(self):
        """
        """
        self._logger.info('{} - start load data from source... '.format(self))

    def __repr__(self):
        """
        pretty print
        """
        return "\n\tLoader ::url {}::db ::folder {}::timeout {}::period {}"\
            .format(self._base_url, self._db_url, self._tmp_folder, \
                self._retry_timeout, self._period)


if __name__ == "__main__":
    pass
