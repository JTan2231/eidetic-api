#!/bin/bash

# Update package index
sudo apt-get update

# Install MySQL Server
sudo apt-get install -y mysql-server

# Start MySQL service
sudo service mysql start

# Secure MySQL installation (optional but recommended)
# sudo mysql_secure_installation

# The following commands assume you have set a password for the MySQL root user during installation
# Replace 'your_root_password' with your actual root password
# Replace 'dev_db' with your development database name
# Replace 'dev_user' and 'dev_password' with your desired development username and password

# Log into MySQL as root, create database, and grant access to new user
sudo mysql -u root -p'your_root_password' <<EOF
CREATE DATABASE dev_db;
CREATE USER 'dev_user'@'localhost' IDENTIFIED BY 'pass';
GRANT ALL PRIVILEGES ON dev_db.* TO 'dev_user'@'localhost';
FLUSH PRIVILEGES;
EOF

echo "MySQL development environment setup complete."

