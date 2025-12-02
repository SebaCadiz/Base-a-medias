# Base-a-medias
SOY MALISIMO PAL GITHUB

sudo apt update
sudo apt install mkcert libnss3-tools -y
mkcert -install

sudo apt install docker.io -y
sudo systemctl enable --now docker
docker compose version
sudo apt install docker-compose-plugin -y


mkcert localhost
python manage.py runserver_plus --cert-file localhost+2.pem --key-file localhost+2-key.pem
docker compose up -d
