"""
    Here settings for application
"""
import os
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

LOG_LEVEL = logging.DEBUG if os.environ.get('DEBUG')\
    else logging.INFO

ENGINE = create_engine(os.environ.get('DB_URL', 'sqlite:///:memory:'))
DB = scoped_session(sessionmaker(bind=ENGINE))
