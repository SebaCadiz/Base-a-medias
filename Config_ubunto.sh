#!/bin/bash
set -e

# =====================================================
# CONFIGURACIÓN GENERAL (MODIFICA SOLO ESTO)
# =====================================================

APP_NAME="NUAM"
DOMAIN="localhost"
DJANGO_PORT=8000

# Ruta base del proyecto (por defecto: donde ejecutas el script)
PROJECT_ROOT="$(pwd)"

# Usuario que ejecuta el script
RUN_USER="$(whoami)"

# Certificados (mkcert u otros)
CERT_FILE="$PROJECT_ROOT/localhost+2.crt"
KEY_FILE="$PROJECT_ROOT/localhost+2.key"

# Archivos estáticos
STATIC_PATH="$PROJECT_ROOT/staticfiles"

APACHE_SITE_CONF="/etc/apache2/sites-available/${APP_NAME,,}_ssl.conf"

# =====================================================
echo "🔧 Configurando Apache HTTPS Proxy para $APP_NAME"
echo "📁 Proyecto: $PROJECT_ROOT"
echo "👤 Usuario: $RUN_USER"
echo "🌐 Dominio: https://$DOMAIN"
echo "================================================="

# =====================================================
# 1. Dependencias
# =====================================================
sudo apt update
sudo apt install -y apache2 apache2-dev python3-dev

# =====================================================
# 2. Módulos Apache necesarios
# =====================================================
sudo a2enmod ssl proxy proxy_http rewrite headers

# =====================================================
# 3. Crear VirtualHost HTTPS con Proxy
# =====================================================
sudo bash -c "cat << EOF > $APACHE_SITE_CONF
<VirtualHost *:443>
    ServerName $DOMAIN

    SSLEngine on
    SSLCertificateFile $CERT_FILE
    SSLCertificateKeyFile $KEY_FILE

    SSLProxyEngine On
    SSLProxyVerify none
    SSLProxyCheckPeerCN off
    SSLProxyCheckPeerName off
    SSLProxyCheckPeerExpire off

    ProxyPreserveHost On
    ProxyRequests Off
    RequestHeader set X-Forwarded-Proto \"https\"

    Alias /static $STATIC_PATH
    <Directory $STATIC_PATH>
        Require all granted
    </Directory>

    ProxyPass /static/ !
    ProxyPass / https://127.0.0.1:$DJANGO_PORT/
    ProxyPassReverse / https://127.0.0.1:$DJANGO_PORT/

    ErrorLog \${APACHE_LOG_DIR}/${APP_NAME,,}_error.log
    CustomLog \${APACHE_LOG_DIR}/${APP_NAME,,}_access.log combined
</VirtualHost>
EOF"

# =====================================================
# 4. Activar sitio y limpiar defaults
# =====================================================
sudo a2ensite "${APP_NAME,,}_ssl.conf"
sudo a2dissite 000-default.conf

# =====================================================
# 5. Permisos mínimos para Apache
# =====================================================
PROJECT_PARENT="$(dirname "$PROJECT_ROOT")"
chmod +x "$PROJECT_PARENT"
chmod +x "$PROJECT_ROOT"

# =====================================================
# 6. Reinicio seguro
# =====================================================
echo "🔄 Verificando configuración Apache..."
sudo apache2ctl configtest
sudo systemctl restart apache2

echo "================================================="
echo "✅ PROCESO FINALIZADO"
echo "🌐 Accede en: https://$DOMAIN"
echo "🚀 Asegúrate de que Django esté corriendo en https://127.0.0.1:$DJANGO_PORT"
echo "================================================="





