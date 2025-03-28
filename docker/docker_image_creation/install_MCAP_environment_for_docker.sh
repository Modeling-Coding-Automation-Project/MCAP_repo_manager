ln -sf /usr/share/zoneinfo/Asia/Tokyo /etc/localtime

apt update -q
apt upgrade -y -q

apt install -y -q build-essential
apt install -y -q x11-apps

# install python3.12
apt install -y -q python3.12 python3.12-venv
python3 -m venv /opt/venv_py_MCAP

source opt/venv_py_MCAP/bin/activate

pip install --upgrade pip
pip install --upgrade setuptools
pip install numpy control matplotlib mplcursors pandas jupyter openpyxl sympy astor python3-tk
apt install -y -q python3-tk
apt install -y -q pybind11-dev

## Clone MCAP repositories
cd /opt
mkdir ModelingCodingAutomationProject
cd ./ModelingCodingAutomationProject

git clone https://github.com/Modeling-Coding-Automation-Project/MCAP_repo_manager.git

cd ./MCAP_repo_manager
chmod +x ./git_supporter/clone_MCAP.py ./git_supporter/update_all_submodules.py

python3 ./git_supporter/clone_MCAP.py --folder /opt/ModelingCodingAutomationProject
python3 ./git_supporter/update_all_submodules.py --folder /opt/ModelingCodingAutomationProject

deactivate
