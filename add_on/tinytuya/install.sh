#!/bin/bash

#app_name:Install TinyTuya
#app_description:Install Support for Tuya WiFi Switches


echo "Check if pip3 is Installed"
var=$(which pip3)
if [ -z "$var" ]
then
  echo "Installing pip3"
  sudo apt-get install python3-pip
else
  echo "pip3 already installed"
fi

echo "Installing tinytuya"
sudo pip3 install tinytuya --break-system-packages --root-user-action=ignore 
