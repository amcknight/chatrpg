# Chat RPG

A minimal Twitch chatbot RPG experiment for https://www.twitch.tv/mangort

## Install

You need Python3.10, pipenv, and git. Detailed instructions below are for EC2.

`sudo yum update -y`

### Python 3.10

 Python installation instructions below are taken from [here](https://www.gcptutorials.com/post/python-3.10-installation-on-amazon-linux-2)

```bash
sudo yum -y groupinstall "Development Tools"
sudo yum -y install gcc devel libffi-devel openssl11 openssl11-devel
wget https://www.python.org/ftp/python/3.10.4/Python-3.10.4.tgz
tar zxvf Python-3.10.4.tgz
rm Python-3.10.4.tgz
cd Python-3.10.4
./configure --enable-optimizations
make
sudo make altinstall
cd ..
```

### Git

```bash
cd ~
mkdir git
cd git
git clone https://github.com/amcknight/chatrpg.git
cd chatrpg
```

### Pipenv

```bash
pip3 install pipenv
pipenv install
```

### Set environment variables

Set these environment variables. I recommend just creating a file called `.env` and putting it in the `chatrpg` folder with these filled in.

```env
TMI_TOKEN=<TMI TOKEN>
CLIENT_ID=<CLIENT ID>
BOT_NICK=<BOT NAME>
CHANNEL=<TWITCH CHANNEL NAME>
```

## Running Chat RPG

### Manually

Simply go into the `chatrpg` directory and run `pipenv run bot`

### As an auto-upgradable service

In the `chatrpg` directory:

```bash
sudo cp chatrpg.service /etc/systemd/system/
sudo systemctl enable chatrpg
sudo systemctl start chatrpg
```

To upgrade, restart the service or server and it will `git pull` before running `pipenv run bot`.
