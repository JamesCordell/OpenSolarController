
sudo apt install -y mariadb-server python3-virtualenv libmariadb3 libmariadb-dev python3-venv

python -m venv .venv

source .venv/bin/activate

pip install -r requirements.txt


useradd -s '/bin/bash' -m -G sudo opensolar

usermod -aG dialout opensolar

sudo cp osTempSensors.service /etc/systemd/system/
sudo cp osWebServer.service /etc/systemd/system/
sudo cp osPumpControl.service /etc/systemd/system/ 

