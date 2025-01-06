#!/bin/bash -e

# Update local G2YS assets from github repo

# Check if git is installed, install it if not already

if ! dpkg -s git >/dev/null 2>&1; then
	echo "Installing git ... "
	sudo apt install -y git
else
	echo "git is already installed!"
fi

# Make sure the directory exists...
DIR="/opt/git/"
if [ ! -d "$DIR" ]; then echo "The directory /opt/git doesn't exist...mkdir 'ing it now ..."
	sudo mkdir $DIR
	sudo chown pi $DIR
else
	echo "The directory /opt/git already exists..."
fi


# Clone the repo into /opt/git/G2YS
cd $DIR
GIT_DIR="$DIR/G2YS"
if [ -d "$GIT_DIR" ]; then
	echo "Local repo already exists ... doing a git pull to update it"
	echo "You will need to enter the password...::"
	cd $GIT_DIR && git pull
else
	echo "First time, eh? Cloning git repo..."
	echo "You will need to enter the password...::"
	git clone https://Taita-Yam@github.com/Taita-Yam/G2YS.git
fi

# Copy the assets
cd $DIR/G2YS
sudo cp ./G2YS/G2YS.py /opt/y/g2ys.py
sudo cp -r ./Web_G2YS/* /var/www/html
sudo cp ./g2ysGitUpdater/updater.sh /home/pi

# Rename this device's hostname to yamahagpio
curr_hostname=`hostname`
new_hostname="yamahagpio"
if [ $curr_hostname != $new_hostname ]; then
	sudo sed -i -e "s/$curr_hostname/$new_hostname/g" /etc/hostname
	sudo sed -i -e "s/$curr_hostname/$new_hostname/g" /etc/hosts
	echo "HOSTNAME HAS BEEN RESET TO: yamahagpio"
	echo "You must reboot for these changes to take effect."
	echo " Please run: sudo reboot"
else
	echo "Hostname will remain unaltered: yamahagpio"
fi

# Restart the systemd g2ys service
sudo systemctl restart g2ys

echo "Update complete..."
