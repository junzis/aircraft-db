#!/bin/bash

# Variables
DBHOST=localhost
DBROOTPASSWD=root
DBPMAPASSWD=phpmyadmin

DBNAME=aircraft
DBUSER=aircraft
DBPASSWD=aircraft

# Change VM name to something simpler
echo vm > /etc/hostname

IPADDR=$(/sbin/ifconfig eth0 | awk '/inet / { print $2 }' | sed 's/addr://')
sed -i "s/^${IPADDR}.*//" hosts
echo $IPADDR vm.local >> /etc/hosts			# Just to quiet down some error messages

# Update the server
echo -e "\n--- Update Server ---\n"
apt-get update
apt-get -y upgrade

# Install basic tools
echo -e "\n--- Install basic packages ---\n"
apt-get -y install build-essential git

# some git setting
git config --global core.filemode false
git config --global user.email "junzi@work.local"
git config --global user.name "Junzi"

# Install Apache
echo -e "\n--- Install Apache, PHP, and moduels ---\n"
apt-get -y install apache2
apt-get -y install php5 php5-curl php5-mysql php5-sqlite php5-mcrypt php5-intl
apt-get -y install libapache2-mod-wsgi

# Install python related stuff
apt-get -y install python-pip
pip install requests beautifulsoup4 flask pymysql

# Install MySQL and PHPMyAdmin
echo -e "\n--- Install MySQL and settings ---\n"
echo "mysql-server mysql-server/root_password password $DBROOTPASSWD" | debconf-set-selections
echo "mysql-server mysql-server/root_password_again password $DBROOTPASSWD" | debconf-set-selections
apt-get -y install mysql-client mysql-server

echo "phpmyadmin phpmyadmin/reconfigure-webserver multiselect apache2" | debconf-set-selections
echo "phpmyadmin phpmyadmin/dbconfig-install boolean true" | debconf-set-selections
echo "phpmyadmin phpmyadmin/mysql/admin-user string root" | debconf-set-selections
echo "phpmyadmin phpmyadmin/mysql/admin-pass password $DBROOTPASSWD" | debconf-set-selections
echo "phpmyadmin phpmyadmin/mysql/app-pass password $DBPMAPASSWD" | debconf-set-selections
echo "phpmyadmin phpmyadmin/app-password-confirm password $DBPMAPASSWD" | debconf-set-selections
apt-get -y install phpmyadmin

# Setup DB for kcloud
echo -e "\n--- Setting up our MySQL user and db ---\n"
mysql -uroot -p$DBROOTPASSWD -e "CREATE DATABASE $DBNAME"
mysql -uroot -p$DBROOTPASSWD -e "grant all privileges on $DBNAME.* to '$DBUSER'@'localhost' identified by '$DBPASSWD'"

# Configuring Apache server
echo -e "\n--- Enabling mod-rewrite ---\n"
a2enmod rewrite > /dev/null 2>&1

echo -e "\n--- Allowing Apache override to all ---\n"
sed -i "s/AllowOverride None/AllowOverride All/g" /etc/apache2/apache2.conf

ln -fs /vagrant /var/www/aif

echo -e "\n--- We definitly want to see the PHP errors, turning them on ---\n"
sed -i "s/error_reporting = .*/error_reporting = E_ALL/" /etc/php5/apache2/php.ini
sed -i "s/display_errors = .*/display_errors = On/" /etc/php5/apache2/php.ini

echo -e "\n--- Add environment variables to Apache ---\n"
cat > /etc/apache2/sites-enabled/000-default.conf <<EOF
<VirtualHost *:80>
    DocumentRoot /var/www
    <Directory /var/www/>
        Options Indexes FollowSymLinks
        AllowOverride All
        Require all granted
    </Directory>
    ErrorLog \${APACHE_LOG_DIR}/error.log
    CustomLog \${APACHE_LOG_DIR}/access.log combined

    WSGIDaemonProcess aif
    WSGIScriptAlias /aif /var/www/aif/app.wsgi

    <Directory /var/www/aif>
            WSGIProcessGroup aif
            WSGIApplicationGroup %{GLOBAL}
            Order deny,allow
            Allow from all
    </Directory>

</VirtualHost>
EOF

echo -e "\n--- Installing Composer for PHP package management ---\n"
curl --silent https://getcomposer.org/installer | php > /dev/null 2>&1
mv composer.phar /usr/local/bin/composer

# Restart Apache2
echo -e "\n--- Restarting Apache Server ---\n"
service apache2 restart > /dev/null 2>&1
