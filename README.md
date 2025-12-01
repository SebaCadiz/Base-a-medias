# Base-a-medias
SOY MALISIMO PAL GITHUB

sudo apt update
sudo apt install wget libnss3-tools -y
wget https://github.com/FiloSottile/mkcert/releases/latest/download/mkcert-linux-amd64
sudo mv mkcert-linux-amd64 /usr/local/bin/mkcert
sudo chmod +x /usr/local/bin/mkcert
mkcert -install
python manage.py runserver_plus --cert-file localhost.pem --key-file localhost-key.pem
mkcert localhost
