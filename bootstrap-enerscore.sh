#!/usr/bin/env bash

#DBHOST=localhost
DBPASSWD=vagrant

DBNAME=rentrocket
DBUSER=rentrocket
DBPASSWD2=greenrentals
GOOGLE_APP_ENGINE_INSTALL_LOCATION=/vagrant
GOOGLE_APP_ENGINE_BASE=google_appengine
GOOGLE_APP_ENGINE_VERSIONED="${GOOGLE_APP_ENGINE_BASE}_1.9.22"
GOOGLE_APP_ENGINE_ARCHIVE="${GOOGLE_APP_ENGINE_VERSIONED}.zip"
GOOGLE_APP_ENGINE_ARCHIVE_URL="https://storage.googleapis.com/appengine-sdks/featured/${GOOGLE_APP_ENGINE_ARCHIVE}"

sudo apt-get update
#sudo apt-get -y upgrade

#http://unix.stackexchange.com/questions/147261/installing-mysql-server-in-vagrant-bootstrap-shell-script-how-to-skip-setup
#debconf-set-selections <<< 'mysql-server mysql-server/root_password password $DBPASSWD'
#debconf-set-selections <<< 'mysql-server mysql-server/root_password_again password $DBPASSWD'

#above version didn't work
echo "mysql-server mysql-server/root_password password $DBPASSWD" | debconf-set-selections
echo "mysql-server mysql-server/root_password_again password $DBPASSWD" | debconf-set-selections

echo "installing mysql server"
sudo apt-get install -y mysql-server

echo "python-mysqldb"
sudo apt-get install -y python-mysqldb

#https://gist.github.com/rrosiek/8190550
echo -e "\n--- Setting up our MySQL user and db ---\n"
#http://dev.mysql.com/doc/refman/5.0/en/create-user.html


mysql -uroot -p$DBPASSWD -e "GRANT ALL PRIVILEGES ON *.* TO '$DBUSER'@'localhost' IDENTIFIED BY '$DBPASSWD2'"
mysql -uroot -p$DBPASSWD -e "DROP USER '$DBUSER'@'localhost'"
mysql -uroot -p$DBPASSWD -e "DROP DATABASE $DBNAME"
mysql -uroot -p$DBPASSWD -e "CREATE USER '$DBUSER'@'localhost' IDENTIFIED BY '$DBPASSWD2'"

mysql -uroot -p$DBPASSWD -e "CREATE DATABASE $DBNAME"
mysql -uroot -p$DBPASSWD -e "grant all privileges on $DBNAME.* to '$DBUSER'@'localhost' identified by '$DBPASSWD2'"

echo "installing python-pip"
sudo apt-get install -y python-pip 

echo "installing unzip"
sudo apt-get install -y unzip

#sudo pip install django
echo "installing django 1.5.11"
sudo pip install django==1.5.11

if [ ! -d "${GOOGLE_APP_ENGINE_INSTALL_LOCATION}/${GOOGLE_APP_ENGINE_BASE}" ]; then

    # echo "Clean up Google App Engine"
    # rm -rf ${GOOGLE_APP_ENGINE_INSTALL_LOCATION}/${GOOGLE_APP_ENGINE_BASE}
    # rm -rf ${GOOGLE_APP_ENGINE_INSTALL_LOCATION}/${GOOGLE_APP_ENGINE_ARCHIVE}

    if [ ! -e "${GOOGLE_APP_ENGINE_ARCHIVE}"]; then
        echo "starting download of appengine zip ${GOOGLE_APP_ENGINE_ARCHIVE}"
        wget -q ${GOOGLE_APP_ENGINE_ARCHIVE_URL}
        echo "finished downloading appengine zip"
    fi

    echo "extracting appengine zip ${GOOGLE_APP_ENGINE_ARCHIVE}"
    unzip -q ${GOOGLE_APP_ENGINE_ARCHIVE} -d ${GOOGLE_APP_ENGINE_INSTALL_LOCATION}

fi 

echo "vagrant environment has been provisioned"
# http://stackoverflow.com/questions/2168409/can-access-appengine-sdk-sites-via-local-ip-address-when-localhost-works-just-fi
#/home/vagrant/google_appengine/dev_appserver.py --host 0.0.0.0 /vagrant

pushd /vagrant

python manage.py syncdb --noinput

python manage.py migrate utility
python manage.py migrate building
python manage.py migrate person
python manage.py migrate city
python manage.py migrate content
python manage.py migrate inspection
python manage.py migrate manager
python manage.py migrate source
python manage.py migrate allauth.socialaccount

pushd ./scripts
python make_cities.py
popd
