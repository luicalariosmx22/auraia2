## 🚀 Deployment de WhatsApp Backend con Chrome en Railway

### 📁 Archivos creados:

1. **`railway-whatsapp-server.js`** - Servidor Node.js con WhatsApp Web
2. **`railway-whatsapp.dockerfile`** - Dockerfile con Chrome
3. **`railway-package.json`** - Dependencias del proyecto

### 🔧 Pasos para deployment:

#### 1️⃣ **Crear nuevo proyecto en Railway:**
   - Ve a [railway.app](https://railway.app)
   - Crea nuevo proyecto desde GitHub
   - Selecciona el repositorio

#### 2️⃣ **Configurar archivos:**
   - Sube `railway-whatsapp-server.js` como `server.js`
   - Sube `railway-package.json` como `package.json`
   - Sube `railway-whatsapp.dockerfile` como `Dockerfile`

#### 3️⃣ **Configurar variables de entorno:**
   ```
   PORT=3000
   CHROME_PATH=/usr/bin/google-chrome-stable
   NODE_ENV=production
   ```

#### 4️⃣ **Deploy:**
   - Railway detectará el Dockerfile automáticamente
   - El build incluirá Chrome
   - ¡WhatsApp Web funcionará con QR real!

### ✅ **Resultado esperado:**
- ✅ Chrome instalado en contenedor
- ✅ QR real generado como imagen PNG
- ✅ WebSocket funcionando perfectamente
- ✅ NORA conectándose sin problemas

### 🔄 **Alternativa rápida:**
Si prefieres actualizar el deployment actual:
1. Reemplaza el `server.js` actual con `railway-whatsapp-server.js`
2. Añade el `Dockerfile` al proyecto
3. Railway rebuild automáticamente

¿Quieres que te ayude con algún paso específico?
