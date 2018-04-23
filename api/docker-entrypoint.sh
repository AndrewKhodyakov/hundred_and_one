#!/bin/sh

#start command
START_PROD_SERVER="gunicorn --bind=$HOST_IP:$SERVER_PORT --workers=$WORKER_COUNT --timeout=$REQ_TIMEOUT app:app"

cd $BASE_DIR

if [ $1 = 'up' ] ; then
    #here database initialization
    python -c "from utils import check_datebase_initialization; check_datebase_initialization()"
    $START_PROD_SERVER
else
    echo 'Set start mode in $1!'
    exit 1
fi
