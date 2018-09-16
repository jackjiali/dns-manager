#!/bin/sh

######################  此脚本docker部署自动调用，请勿手动运行！  ########################
sleep 5
export FLASK_APP=${PWD}/app.py
export FLASK_DEBUG=0
PEB_PORT=$1
MYSQL_HOST_PORT=$2
USER=$3
PASSWORD=$4
DB_NAME=$5

while true;do
    echo $i
    echo "################   mysql initing...   #######################"
    python /code/docs/install/checkdb.py ${MYSQL_HOST_PORT} ${USER} ${PASSWORD} ${DB_NAME} > /dev/null 2>&1
    ready=$?
    if [ $ready -eq 0 ];then
        break
    fi
    sleep 1
done

echo "################# mysql init done!!!  #######################"

if [ ! -d migrations ];then
    echo "migration not exists!!!!!"
    flask db init
    flask db migrate
    flask db upgrade
    flask initdb
fi

echo "################# init db data done!!!  #######################"

gunicorn -w 4 app:app -b 0.0.0.0:${PEB_PORT} \
        --log-level=debug \
        --access-logfile logs/peb_dns_access.log \
        --error-logfile logs/peb_dns_error.log \
        --log-file logs/peb_dns.log

echo "################# peb_dns started !!!  #######################"
