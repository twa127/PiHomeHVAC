#!/bin/bash
#service_name:HA_integration.service
#app_name:Install Home Assistant Integration
#app_description:This add-on requires Home Assistant with Mosquito Broker running on a separate device.

PYTHON3DEV=$( apt-cache pkgnames python3-dev )
if [[ $PYTHON3DEV == *"python3-dev"* ]]; then
  echo "Python3-dev is already installed"
else
  echo "Installing Python3-dev"
  sudo apt-get install -y python3-dev
fi

echo "Installing Phyton modules"
MODEL=$(tr -d '\0' </proc/device-tree/model)
if [[ $MODEL == *"Raspberry"* ]]; then
  echo "Model: Raspberry"
  NUMPY=$( pip3 list|grep numpy|awk '{print $1}' )
  if [[ $NUMPY == "numpy" ]]; then
    echo "Python numpy already installed"
  else
    echo "Installing Python numpy"
    sudo pip3 install numpy --break-system-packages --root-user-action=ignore
  fi
  sudo pip3 install paho-mqtt --break-system-packages --root-user-action=ignore
  sudo pip3 install psutil --break-system-packages --root-user-action=ignore
  sudo pip3 install pytz==2019.2 --break-system-packages --root-user-action=ignore
  sudo pip3 install PyYAML --break-system-packages --root-user-action=ignore
  sudo pip3 install rpi_bad_power==0.1.0 --break-system-packages --root-user-action=ignore
else
  NUMPY=$( pip3 list|grep numpy|awk '{print $1}' )
  if [[ $NUMPY == "numpy" ]]; then
    echo "Python numpy already installed"
  else
    echo "Installing Python numpy"
    sudo pip3 install numpy --break-system-packages --root-user-action=ignore
  fi
  sudo pip3 install paho-mqtt
  sudo pip3 install psutil
  sudo pip3 install pytz
  sudo pip3 install PyYAML
fi

echo "Creating service for auto start"
sudo cp /var/www/add_on/HomeAssistant/HA_integration.service /etc/systemd/system/HA_integration.service
sudo systemctl enable HA_integration.service

echo "Starting the service"
sudo systemctl start HA_integration.service
