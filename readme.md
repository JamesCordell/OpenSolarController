
sudo apt install -y mariadb-server python3-virtualenv libmariadb3 libmariadb-dev

python -m venv .venv

source .venv/bin/activate

pip install -r requirements.txt


