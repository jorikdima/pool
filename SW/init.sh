sudo apt update
sudo apt full-upgrade -y
sudo apt install wavemon mc libgpiod-dev cmake -y

sudo timedatectl set-timezone America/Los_Angeles

"
dtoverlay=ads1015
dtparam=cha_enable=1,cha_cfg=1,cha_datarate=0,cha_gain=3
dtparam=chb_enable=1,chb_cfg=2,chb_datarate=0,chb_gain=3
"
