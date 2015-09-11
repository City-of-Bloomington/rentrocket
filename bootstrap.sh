#!/usr/bin/env bash

#DBHOST=localhost
DBPASSWD=vagrant

DBNAME=rentrocket
DBUSER=rentrocket
DBPASSWD2=greenrentals

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

#https://cloud.google.com/appengine/downloads
echo "starting download of appengine zip"
wget -q https://storage.googleapis.com/appengine-sdks/featured/google_appengine_1.9.22.zip
echo "finished downloading appengine zip"

echo "extracting appengine zip"
unzip -q google_appengine_1.9.22.zip -d /vagrant

echo "vagrant environment has been provisioned"
# http://stackoverflow.com/questions/2168409/can-access-appengine-sdk-sites-via-local-ip-address-when-localhost-works-just-fi
#/home/vagrant/google_appengine/dev_appserver.py --host 0.0.0.0 /vagrant
