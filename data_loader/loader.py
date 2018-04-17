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

        self._logger.info('Create logger and read ENVs...')

        self._from_date = os.environ.get('FROM_DATE', '')
        self._to_date = os.environ.get('TO_DATE', '')
        self._base_url = os.environ.get('SOURSE_URL', '')
        self._db_url = os.environ.get('DB_URL', '')
        self._db = None
        self._tmp_folder = os.environ.get('TMP_FOLDER', '../tmp')
        self._retry_timeout = int(os.environ.get('RETRY_TIMEOUT', '10'))

        if not self._from_date and not self._to_date:
            raise AttributeError('FROM_DATE and TO_DATE envs are not defined')

        if not self._base_url:
            raise AttributeError('SOURSE_URL env is not defined')

        if not self._db_url:
            raise AttributeError('DB_URL env is not defined')

        if not os.path.exists(self._tmp_folder):
            raise AttributeError('TMP_FOLDER - {}, is not existst'.format(self._tmp_folder))

    def run(self):
        """
        run loader
        """
        pass

    def _get_db_connect(self):
        """
        Create db connection
        """
        pass

    def _load_data(self):
        """
        """
        pass

    def __repr__(self):
        """
        pretty print
        """
        return "\n\tLoader ::url {}::db ::folder {}::timeout {}::dates {} - {}"\
            .format(self._base_url, self._db_url, self._tmp_folder, \
                self._retry_timeout, self._from_date, self._to_date)


if __name__ == "__main__":
    pass
