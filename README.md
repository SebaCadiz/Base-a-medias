#README Completo del Proyecto NUAM
Este documento describe detalladamente el proceso completo para instalar, configurar y ejecutar el proyecto NUAM, tanto en Windows como en Linux., comandos separados por sistema operativo, configuraciones necesarias de HTTPS mediante mkcert, uso de entornos virtuales, ejecución local y levantamiento mediante Docker.

📌 Información General del Proyecto
NUAM es un sistema desarrollado en Django que incluye integración con Apache Pulsar, herramientas de desarrollo avanzadas, ejecución segura mediante certificados HTTPS y despliegue con Docker. Este proyecto fue elaborado por el equipo compuesto por:

👥 Integrantes
Nicolás Lobos
Sebastián Cádiz
Nicolás Sepúlveda
José Anabalón
📁 Estructura del Proyecto
El repositorio contiene:
Código fuente Django
Templates
static
apis
Archivos requirements.txt
Archivos de Docker (docker-compose.yml, Dockerfile)
Configuración avanzada de desarrollo con django-extensions y runserver_plus
📦 Dependencias del Proyecto
Estas se encuentran definidas en requirements.txt:
Django>=4.2
pulsar-client==3.4.0
requests
docker
pyOpenSSL
django-extensions
Werkzeug

Estas librerías permiten soporte para:
Servidor de desarrollo avanzado con HTTPS
Ejecución de productores/consumidores Pulsar
Integración directa con Docker desde Python
Utilidades para depurar y extender Django


📥 Instalación del Proyecto
A continuación se presentan los pasos completos.


1️⃣ Utilizar un progama como visual studio code o similiraes como tambien la teminal y power shell
  Entrar al proyecto
  cd Proyecto_Nuam-main
🌱 2️⃣ Crear un entorno virtual (environment)
Es obligatorio para aislar las dependencias debe crear un entorno virtual cerca del proyecto ademas se nesita tener descargado python y pip para funcionar.

Windows
Simbolo del sistema,Comand Pront
python -m venv env
env\Scripts\activate
pip install -r requirements.txt

Linux
Terminal:
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt
⚠️ Cada vez que se trabaje en el proyecto debe activarse el entorno virtual.

🔐 3️⃣ Instalación de mkcert (HTTPS Local)
mkcert permite crear certificados HTTPS locales confiables, requeridos para ejecutar Django con runserver_plus.

Linux
ejecutar en terminal por defecto:
sudo apt update
sudo apt install mkcert libnss3-tools -y
mkcert -install

Windows
ejecutar en PowerShell como administrador: 
Descargar mkcert desde el sitio oficial: 
Set-ExecutionPolicy Bypass -Scope Process -Force; `iwr https://community.chocolatey.org/install.ps1 -UseBasicParsing | iex 
choco install mkcert 
mkcert -install

🔏 4️⃣ Generar certificados HTTPS
Estos archivos deben quedar en el directorio principal del proyecto. Se deben generar los certificados para localhost.
en el Simbolo de sistema(Comand Pront) o terminal(Linux)
EN solo la raíz Proyecto_Nuam-main

Escribe esto cuando tengas la pagina corriendo:
mkcert localhost 127.0.0.1

Esto crea archivos similares a:
localhost.cert
localhost.key
localhost+1-key.pem
localhost+1.pem

🐳 5️⃣ Docker: Instalación y Uso
El proyecto puede ser ejecutado mediante Docker para mayor estabilidad.

🔹 Windows — Docker Desktop
Descargar desde: 👉 https://www.docker.com/products/docker-desktop/

Instalar y luego reiniciar el sistema si se solicita.

🔹 Linux 
sudo apt update
sudo apt install docker.io docker-compose -y
sudo systemctl enable docker
sudo systemctl start docker
sudo usermod -aG docker $USER
(Cerrar sesión y volver a entrar o simplemente reinicia)

Docker es el primer servicio que se debe levantar cuando se trabaja en modo contenedores.
Desde la raíz del Proyecto_Nuam-main/pulsar-docker en el Simbolo de sistema (Comand Pront) o Teminal(Linux) ejecutar:
docker compose up -d
Esto levanta todos los servicios definidos dentro de docker-compose.yml.
Para detener:
docker compose down

6️⃣ Para hacer correr ahora la pagina ejecutar el comando:
Usar simbolo del sistema (Comand Pront) antes de ejecutar cualquiero comando, asegurandose de estar en la raíz del proyecto(\Proyecto_Nuam-main).
python manage.py runserver_plus --cert-file localhost.pem
esto levanta el servidor y genera lo siguiente:

WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.
 * Running on https://127.0.0.1:8000 SELECIONAR ESTO PARA INGRESAR RAPIDO A LA PAGINA
 
Press CTRL+C to quit
 * Restarting with stat
Performing system checks...
System check identified no issues (0 silenced).
Django version 5.1.3, using settings 'NUAM.settings'
Development server is running at https://[127.0.0.1]:8000/
Using the Werkzeug debugger (https://werkzeug.palletsprojects.com/)
Quit the server with CTRL-BREAK.
O EN EL NAVEGADOR COLOCAR https://127.0.0.1:8000
esto lo enviara directamente al la pagina web

Al momento de ingresar a al link de la terminal, la pagina se iniciara con un error de seguridad
Presionar opciones avanzadas, luego presionar continuar a 127.0.0.1:8000/

Si quiere entrar al modo admin es
https://127.0.0.1:8000/admin/

Para deterner el proyecto, en la terminal donde se ejecuta usar el comando CTRL + C 
▶️ 7️⃣ Orden Correcto para Ejecutar el Proyecto
El proyecto debe iniciarse en el siguiente orden:
Activar el entorno virtual (solo para desarrollo local).
Generar certificados HTTPS con mkcert (solo la primera vez).
Levantar Docker primero. Docker debe iniciarse antes que el servidor Django porque contiene los servicios base necesarios.
Ejecutar Django con HTTPS, solo si se trabaja fuera de Docker.
📂 Ubicación de Archivos y Dónde Ejecutar los Comandos
Todos los comandos se ejecutan en la raíz del proyecto, es decir, donde se encuentra:

manage.py
requirements.txt
docker-compose.yml
Certificados localhost+2.pem y localhost+2-key.pem
Ejemplo de estructura:

NUAM/
│── manage.py
│── docker-compose.yml
│── requirements.txt
│── localhost+2.pem
│── localhost+2-key.pem
│── app/        ← carpeta Django
│── ...
Comandos que van en la raíz del proyecto
Acción	Comando	Ubicación
Activar entorno	env/Scripts/activate o source env/bin/activate	raíz del proyecto
Instalar dependencias	pip install -r requirements.txt	raíz
Generar certificados	mkcert localhost	raíz
Ejecutar Django HTTPS	python manage.py runserver_plus ...	raíz

📘 Recomendaciones Finales
Activar siempre el entorno virtual antes de ejecutar Django.
No borrar los certificados generados por mkcert.
docker compose up -d se utiliza para entornos de prueba o producción local.
Para cambios en contenedores reconstruir con:
docker compose build --no-cache
Para migraciones Django (si no usa Docker):
python manage.py migrate
Fin del Documento
