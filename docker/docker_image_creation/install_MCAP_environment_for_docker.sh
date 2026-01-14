ln -sf /usr/share/zoneinfo/Asia/Tokyo /etc/localtime

apt update -q
apt upgrade -y -q

apt install -y -q curl \
    wget \
    gnupg \
    apt-transport-https \
    software-properties-common \
    libx11-xcb1 \
    libxkbfile1 \
    libsecret-1-0 \
    libgtk-3-0 \
    libnss3 \
    libxss1 \
    libasound2 \
    xdg-utils \
    unzip \

apt update -q

apt install -y -q git
apt install -y -q build-essential
apt install -y -q cmake
apt install -y -q gdb
apt install -y -q x11-apps
apt install -y -q xvfb
apt install -y -q clang-format
apt install -y -q nano
apt install -y -q pybind11-dev
apt install -y -q fonts-noto-cjk

# install python3.12
apt install -y -q python3.12 python3.12-dev python3.12-venv
python3 -m venv /opt/venv_py_MCAP

/opt/venv_py_MCAP/bin/pip install --upgrade pip
/opt/venv_py_MCAP/bin/pip install --upgrade setuptools
/opt/venv_py_MCAP/bin/pip install numpy scipy control matplotlib mplcursors pandas jupyter openpyxl sympy astor pybind11 networkx dill requests
apt install -y -q python3-tk

## Clone MCAP repositories
cd /opt
mkdir ModelingCodingAutomationProject
cd ./ModelingCodingAutomationProject

git clone https://github.com/Modeling-Coding-Automation-Project/MCAP_repo_manager.git

cd ./MCAP_repo_manager/git_supporter
chmod +x clone_MCAP.py update_all_submodules.py

cd ../

/opt/venv_py_MCAP/bin/python3 ./git_supporter/clone_MCAP.py --folder /opt/ModelingCodingAutomationProject
/opt/venv_py_MCAP/bin/python3 ./git_supporter/update_all_submodules.py --folder /opt/ModelingCodingAutomationProject

rm -rf /var/lib/apt/lists/*
