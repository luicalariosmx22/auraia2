#!/bin/bash
# ===========================================
# Script para ejecutar NORA con entorno virtual
# ===========================================

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Iniciando NORA con entorno virtual...${NC}"

# Verificar que estamos en el directorio correcto
if [ ! -f "app.py" ]; then
    echo -e "${RED}❌ Error: No se encontró app.py. Ejecuta desde el directorio raíz de NORA${NC}"
    exit 1
fi

# Verificar que existe el entorno virtual
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}⚠️ Creando entorno virtual...${NC}"
    python3 -m venv venv
    
    echo -e "${YELLOW}📦 Instalando dependencias...${NC}"
    source venv/bin/activate
    pip install -r requirements.txt
    
    # Instalar dependencias específicas de WhatsApp Web
    pip install python-socketio[client] requests python-dotenv
    
    echo -e "${GREEN}✅ Entorno virtual configurado${NC}"
else
    echo -e "${GREEN}✅ Entorno virtual encontrado${NC}"
fi

# Activar entorno virtual
echo -e "${YELLOW}🔄 Activando entorno virtual...${NC}"
source venv/bin/activate

# Verificar dependencias críticas
echo -e "${YELLOW}🔍 Verificando dependencias...${NC}"
python3 -c "
import sys
try:
    import flask
    import socketio
    import requests
    from dotenv import load_dotenv
    print('✅ Dependencias básicas OK')
except ImportError as e:
    print(f'❌ Error de dependencias: {e}')
    sys.exit(1)

try:
    from clientes.aura.utils.whatsapp_websocket_client import WhatsAppWebSocketClient
    print('✅ Cliente WhatsApp Web OK')
except ImportError as e:
    print(f'❌ Error cliente WhatsApp: {e}')
    sys.exit(1)
"

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Error en verificación de dependencias${NC}"
    exit 1
fi

# Configurar variables de entorno
echo -e "${YELLOW}🔧 Configurando variables de entorno...${NC}"
export FLASK_APP=app.py
export FLASK_ENV=development
export WHATSAPP_BACKEND_URL_PUBLIC="https://whatsapp-server-production-8f61.up.railway.app"
export WHATSAPP_BACKEND_URL_INTERNAL="https://whatsapp-server.railway.internal"

# Ejecutar NORA
echo -e "${GREEN}🌟 Ejecutando NORA...${NC}"
echo -e "${YELLOW}📱 WhatsApp Backend: ${WHATSAPP_BACKEND_URL_PUBLIC}${NC}"
echo -e "${YELLOW}🔗 Panel: http://localhost:5000${NC}"
echo -e "${YELLOW}📊 WhatsApp Web: http://localhost:5000/panel_cliente/aura/whatsapp${NC}"

# Iniciar con gunicorn si está disponible, sino con Flask dev server
if command -v gunicorn &> /dev/null; then
    echo -e "${GREEN}🚀 Iniciando con Gunicorn...${NC}"
    gunicorn -w 4 -b 0.0.0.0:5000 app:app
else
    echo -e "${YELLOW}🔄 Iniciando con Flask dev server...${NC}"
    python3 app.py
fi
