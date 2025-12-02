# README Completo del Proyecto NUAM

Este documento describe detalladamente el proceso completo para instalar, configurar y ejecutar el proyecto **NUAM**, tanto en Windows como en Linux., comandos separados por sistema operativo, configuraciones necesarias de HTTPS mediante **mkcert**, uso de **entornos virtuales**, ejecución local y levantamiento mediante **Docker**.

---

# 📌 Información General del Proyecto

NUAM es un sistema desarrollado en **Django** que incluye integración con **Apache Pulsar**, herramientas de desarrollo avanzadas, ejecución segura mediante certificados HTTPS y despliegue con Docker. Este proyecto fue elaborado por el equipo compuesto por:

### 👥 Integrantes

* **Nicolás Lobos**
* **Sebastián Cádiz**
* **Nicolás Sepúlveda**
* **José Anabalón**

---

# 📁 Estructura del Proyecto

El repositorio contiene:

* Código fuente Django
* Archivos `requirements.txt`
* Archivos de Docker (`docker-compose.yml`, Dockerfile)
* Certificados HTTPS generados por mkcert
* Configuración avanzada de desarrollo con `django-extensions` y `runserver_plus`

---

# 📦 Dependencias del Proyecto

Estas se encuentran definidas en `requirements.txt`:

```
Django>=4.2
pulsar-client==3.4.0
requests
docker
pyOpenSSL
django-extensions
Werkzeug
```

Estas librerías permiten soporte para:

* Servidor de desarrollo avanzado con HTTPS
* Ejecución de productores/consumidores Pulsar
* Integración directa con Docker desde Python
* Utilidades para depurar y extender Django

---

# 📥 Instalación del Proyecto

A continuación se presentan los pasos completos.

## 1️⃣ Clonar el repositorio

```
git clone <URL_DEL_REPOSITORIO>
cd NUAM
```

---

# 🌱 2️⃣ Crear un entorno virtual (environment)

Es obligatorio para aislar las dependencias debe crear un entorno virtual cerca del proyecto.

## Windows

```
python -m venv env
env\Scripts\activate
pip install -r requirements.txt
```

## Linux

```
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt
```

⚠️ *Cada vez que se trabaje en el proyecto debe activarse el entorno virtual.*

---

# 🔐 3️⃣ Instalación de mkcert (HTTPS Local)

mkcert permite crear certificados HTTPS locales confiables, requeridos para ejecutar Django con `runserver_plus`.

## Linux (Ubuntu/Debian)
ejecutar en terminal:
```
sudo apt update
sudo apt install mkcert libnss3-tools -y
mkcert -install
```

## Windows
ejecutar en PowerShell:
Descargar mkcert desde el sitio oficial:
Set-ExecutionPolicy Bypass -Scope Process -Force; `iwr https://community.chocolatey.org/install.ps1 -UseBasicParsing | iex
choco install mkcert
mkcert -install



---

# 🔏 4️⃣ Generar certificados HTTPS
Estos archivos deben quedar en el directorio principal del proyecto.
Se deben generar los certificados para `localhost`.

```
mkcert localhost
```

Esto crea archivos similares a:

```
localhost+2.pem
localhost+2-key.pem
```

---

# 🚀 5️⃣ Ejecutar el servidor Django con HTTPS

El proyecto utiliza `runserver_plus` para soportar certificados.

```
python manage.py runserver_plus --cert-file localhost+2.pem --key-file localhost+2-key.pem
```

Al iniciar, el servidor queda disponible en:
🔗 [https://localhost:8000](https://localhost:8000)

---

# 🐳 6️⃣ Docker: Instalación y Uso

El proyecto puede ser ejecutado mediante Docker para mayor estabilidad.

## 🔹 Windows — Docker Desktop

Descargar desde:
👉 [https://www.docker.com/products/docker-desktop/](https://www.docker.com/products/docker-desktop/)

Instalar y luego reiniciar el sistema si se solicita.

## 🔹 Linux (Ubuntu)

```
sudo apt update
sudo apt install docker.io docker-compose -y
sudo systemctl enable docker
sudo systemctl start docker

```

### Opcional: permitir docker sin sudo

```
sudo usermod -aG docker $USER
```

(Cerrar sesión y volver a entrar o simplemente reinicia)

---

# ▶️ 7️⃣ Orden Correcto para Ejecutar el Proyecto

El proyecto **debe iniciarse en el siguiente orden**:

1. **Activar el entorno virtual** (solo para desarrollo local).
2. **Generar certificados HTTPS con mkcert** (solo la primera vez).
3. **Levantar Docker primero.**
   Docker debe iniciarse antes que el servidor Django porque contiene los servicios base necesarios.
4. **Ejecutar Django con HTTPS**, solo si se trabaja fuera de Docker.

---

# 📂 Ubicación de Archivos y Dónde Ejecutar los Comandos

Todos los comandos se ejecutan en la **raíz del proyecto**, es decir, donde se encuentra:

* `manage.py`
* `requirements.txt`
* `docker-compose.yml`
* Certificados `localhost+2.pem` y `localhost+2-key.pem`

Ejemplo de estructura:

```
NUAM/
│── manage.py
│── docker-compose.yml
│── requirements.txt
│── localhost+2.pem
│── localhost+2-key.pem
│── app/        ← carpeta Django
│── ...
```

### Comandos que van en la raíz del proyecto

| Acción                | Comando                                            | Ubicación         |
| --------------------- | -------------------------------------------------- | ----------------- |
| Activar entorno       | `env/Scripts/activate` o `source env/bin/activate` | raíz del proyecto |
| Instalar dependencias | `pip install -r requirements.txt`                  | raíz              |
| Generar certificados  | `mkcert localhost`                                 | raíz              |
| Ejecutar Django HTTPS | `python manage.py runserver_plus ...`              | raíz              |
| Levantar Docker       | `docker compose up -d`                             | raíz              |

---

# 🐳 7️⃣ Levantar el proyecto con Docker

Docker es el primer servicio que se debe levantar cuando se trabaja en modo contenedores.

Desde la **raíz del proyecto NUAM** ejecutar:

```
docker compose up -d
```

Esto levanta todos los servicios definidos dentro de `docker-compose.yml`.

Para detener:

```
docker compose down
```

Desde la raiz del proyecto ejecutar:

```
docker compose up -d
```

Esto inicia todos los servicios necesarios.

Para detener:

```
docker compose down
```

---

# 🧪 8️⃣ Pruebas y Depuración

El entorno cuenta con herramientas como:

* `django-extensions` → comandos adicionales
* `shell_plus` → consola mejorada
* `runserver_plus` → debugging mejorado y HTTPS

Ejemplo:

```
python manage.py shell_plus
```

---

# 📘 Recomendaciones Finales

* Activar siempre el entorno virtual antes de ejecutar Django.
* No borrar los certificados generados por mkcert.
* `docker compose up -d` se utiliza para entornos de prueba o producción local.
* Para cambios en contenedores reconstruir con:

```
docker compose build --no-cache
```

* Para migraciones Django (si no usa Docker):

```
python manage.py migrate
```

---

# Fin del Documento
