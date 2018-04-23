"""
    Here settings for application
"""
import os
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from utils import check_datebase_initialization

LOG_LEVEL = logging.DEBUG if os.environ.get('DEBUG')\
    else logging.INFO

ENGINE = create_engine(os.environ.get('DB_URL', 'sqlite:///:memory:'))
check_datebase_initialization(ENGINE, LOG_LEVEL)
DB = scoped_session(sessionmaker(bind=ENGINE))
