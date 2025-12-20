el README completo del Proyecto NUAM:

* Uso **obligatorio del archivo `.env`**
* Aclaración de que la **API Key está en un Word externo** (no en GitHub)
* Uso de un **Excel de prueba para carga masiva**
* **Primero Docker + Apache en Windows**
* **Linux usando `Configurar_Ubunto.sh`**
* **Reinicio obligatorio**
* **Uso de dos terminales** (worker + servidor Django)

---

# 📘 README Completo del Proyecto NUAM

Este documento describe detalladamente el proceso completo para **instalar, configurar y ejecutar el proyecto NUAM**, tanto en **Windows como en Linux**, incluyendo **uso de variables de entorno**, **HTTPS con mkcert**, **Docker**, **Apache**, **entornos virtuales** y **ejecución correcta de servicios**.

---

## 📌 Información General del Proyecto

**NUAM** es un sistema desarrollado en **Django**, con integración a **Apache Pulsar**, ejecución segura mediante **HTTPS**, y despliegue mediante **Docker**.

### 👥 Integrantes

* Nicolás Lobos
* Sebastián Cádiz
* Nicolás Sepúlveda
* José Anabalón

---

## 📁 Estructura del Proyecto

El repositorio contiene:

* Código fuente Django
* Templates
* static
* staticfiles
* apis
* apache / httpd
* requirements.txt
* docker-compose.yml
* Dockerfile
* Configuración avanzada con `django-extensions` y `runserver_plus`

---

## 📦 Dependencias del Proyecto

Definidas en `requirements.txt`:

* Django>=5.1.3
* pulsar-client==3.4.0
* requests
* docker
* pyOpenSSL
* django-extensions
* Werkzeug
* openpyxl
* pandas
* safety
* defusedxml
* whitenoise
* FastAPI
* uvicorn
* python-dotenv
* pydantic
* email-validator
* python-decouple
* mod_wsgi

Estas librerías permiten:

* Servidor avanzado con HTTPS
* Productores/consumidores Pulsar
* Integración Docker
* Depuración avanzada Django

---

# 🟢 PASO 1 — Creación y Uso de Variables de Entorno (.env)

⚠️ **OBLIGATORIO – PRIMER PASO**

En la **raíz del proyecto** crear un archivo llamado exactamente:

```
.env
```

### 📄 Contenido del archivo `.env`

```env
DEBUG=false

# Apache Pulsar
PULSAR_URL=pulsar://localhost:6650
EMAIL_TOPIC=persistent://public/default/email

# Email
SMTP_HOST=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USER=apikey
SMTP_PASS=API_KEY_NO_PUBLICA
DEFAULT_NOTIFICATION_EMAIL=pruebas.nuam@gmail.com
```

📌 **IMPORTANTE**

* La **API KEY NO SE SUBE A GITHUB**
* La API Key se encuentra en un **archivo Word externo**, entregado por el equipo
* GitHub borra o invalida credenciales automáticamente

---

## 📊 Excel de Prueba para Carga Masiva

El proyecto utiliza un **archivo Excel de prueba** para cargas masivas de datos.
Se adjunto un archivo de prueba para el trabajo

* El archivo debe estar en formato `.xlsx`
* Se utiliza junto a `openpyxl` y `pandas`

---

# 🟢 PASO 2 — Instalación de Docker y Apache (WINDOWS)

## 🐳 Docker Desktop (Windows)

1. Descargar desde:
   👉 [https://www.docker.com/products/docker-desktop/](https://www.docker.com/products/docker-desktop/)
2. Instalar
3. **Reiniciar el sistema**

---

## 🌐 Apache 2.4 (Windows)

Descargar desde:
👉 [https://www.apachelounge.com/download/](https://www.apachelounge.com/download/)

### Comandos básicos

```bash
httpd.exe -k start
httpd.exe -k stop
httpd.exe -k restart
```

---

### 📄 `httpd.conf` (Configuración)

```apache
Define SRVROOT "C:/Apache24"
ServerRoot "${SRVROOT}"

Listen 443
ServerAdmin admin@localhost
ServerName localhost:443
```

### Módulos requeridos

```apache
LoadModule proxy_module modules/mod_proxy.so
LoadModule proxy_http_module modules/mod_proxy_http.so
LoadModule ssl_module modules/mod_ssl.so
LoadModule rewrite_module modules/mod_rewrite.so
```

⚠️ **NO DEFINAS DocumentRoot GLOBAL**

---

### 🔐 VirtualHost HTTPS

```apache
<VirtualHost *:443>
    ServerName localhost

    SSLEngine on
    SSLCertificateFile "C:/Apache24/conf/certs/localhost+1.pem"
    SSLCertificateKeyFile "C:/Apache24/conf/certs/localhost+1-key.pem"

    ProxyPreserveHost On
    ProxyRequests Off
    RequestHeader set X-Forwarded-Proto "https"

    ProxyPass /static/ !
    ProxyPass / http://127.0.0.1:8000/
    ProxyPassReverse / http://127.0.0.1:8000/
</VirtualHost>
```

---

# 🟢 PASO 3 — Linux (Ubuntu) – Configuración Automática

En Linux **NO se configura manualmente**.

Desde la raíz del proyecto:

```bash
chmod +x Configurar_Ubunto.sh
sudo ./Configurar_Ubunto.sh
```

✔ Este script instala:
* Docker
* Docker Compose
* Apache
* Dependencias del sistema

🔴 **REINICIAR EL SISTEMA DESPUÉS DE EJECUTAR EL SCRIPT**

---

# 🟢 PASO 4 — Instalación de mkcert (HTTPS Local)

## Windows (PowerShell como administrador)

```powershell
Set-ExecutionPolicy Bypass -Scope Process -Force
iwr https://community.chocolatey.org/install.ps1 -UseBasicParsing | iex
choco install mkcert
mkcert -install
```

## Linux

```bash
sudo apt update
sudo apt install mkcert libnss3-tools -y
mkcert -install
```

---

## 🔏 Generar Certificados HTTPS

Desde la **raíz del proyecto**:

```bash
mkcert localhost 127.0.0.1
```

Genera archivos como:

* localhost+2.pem
* localhost+2-key.pem

⚠️ **NO BORRAR ESTOS ARCHIVOS**

---

# 🟢 PASO 5 — Crear y Activar Entorno Virtual

## Windows

```bash
python -m venv env
env\Scripts\activate
pip install -r requirements.txt
```

## Linux

```bash
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt
```

⚠️ **Siempre activar el entorno virtual antes de trabajar**

---

# 🟢 PASO 6 — Levantar Docker (OBLIGATORIO)

Desde:

```
Proyecto_Nuam-main/pulsar-docker
```

```bash
docker compose up -d
```

Para detener:

```bash
docker compose down
```

---

# 🟢 PASO 7 — Ejecución Correcta (2 TERMINALES)

## 🖥 Terminal 1 — Worker Pulsar

Desde la carpeta `miapp`:

```bash
python worker.py
```

⚠️ **Debe quedar corriendo**

---

## 🖥 Terminal 2 — Servidor Django HTTPS

Desde la **raíz del proyecto**:

```bash
python manage.py runserver_plus --cert-file localhost+2.pem
```

Salida esperada:

```
Running on https://127.0.0.1:8000
```

---

## 🌐 Accesos

* Página principal:
  👉 https://localhost

* Admin:
  👉 https://localhost/admin/ solo disponible ya inciado dentro de la pagina
  
⚠️ Al ingresar por primera vez:
Cree un perfil enbase a su correo para el funcionamiento del micro servicio

---

# ▶️ ORDEN CORRECTO FINAL

1. Crear `.env`
2. Instalar Docker + Apache
3. Configurar Linux o Windows
4. Instalar mkcert
5. Generar certificados
6. Crear entorno virtual
7. Levantar Docker
8. Ejecutar `worker.py`
9. Ejecutar Django con HTTPS

---

## 📘 Recomendaciones Finales

* Activar siempre el entorno virtual
* No subir `.env` ni credenciales
* Reiniciar después de instalaciones grandes
* Para cambios en Docker:

```bash
docker compose build --no-cache
```

* Migraciones Django:

```bash
python manage.py migrate
```

---

✅ **Fin del Documento – README Oficial Proyecto NUAM**
