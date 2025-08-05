#!/bin/bash

# Verificación de archivos para Railway deployment
echo "=== VERIFICACIÓN DE ARCHIVOS PARA RAILWAY ==="
echo "Fecha: $(date)"
echo ""

# Archivos críticos para Railway
CRITICAL_FILES=(
    "server.js"
    "package.json"
    "Dockerfile"
)

# Directorio del proyecto
PROJECT_DIR="/mnt/c/Users/PC/PYTHON/Auraai2"
cd "$PROJECT_DIR"

echo "📁 Directorio del proyecto: $PROJECT_DIR"
echo ""

# Verificar cada archivo crítico
echo "🔍 VERIFICANDO ARCHIVOS CRÍTICOS:"
echo "-----------------------------------"

for FILE in "${CRITICAL_FILES[@]}"; do
    if [ -f "$FILE" ]; then
        SIZE=$(stat -c%s "$FILE")
        echo "✅ $FILE - Tamaño: $SIZE bytes"
        
        # Verificaciones específicas
        case "$FILE" in
            "server.js")
                echo "   📝 Verificando contenido de server.js..."
                if grep -q "process.env.PORT" "$FILE"; then
                    echo "   ✅ Puerto configurado correctamente"
                else
                    echo "   ⚠️  Puerto podría no estar configurado"
                fi
                
                if grep -q "express" "$FILE"; then
                    echo "   ✅ Express detectado"
                else
                    echo "   ❌ Express no detectado"
                fi
                ;;
                
            "package.json")
                echo "   📝 Verificando package.json..."
                if grep -q '"start"' "$FILE"; then
                    echo "   ✅ Script de start definido"
                else
                    echo "   ⚠️  Script de start podría faltar"
                fi
                
                if grep -q '"main"' "$FILE"; then
                    echo "   ✅ Main entry point definido"
                else
                    echo "   ⚠️  Main entry point podría faltar"
                fi
                ;;
                
            "Dockerfile")
                echo "   📝 Verificando Dockerfile..."
                if grep -q "google-chrome" "$FILE"; then
                    echo "   ✅ Chrome installation detectada"
                else
                    echo "   ⚠️  Chrome installation podría faltar"
                fi
                ;;
        esac
    else
        echo "❌ $FILE - NO ENCONTRADO"
    fi
    echo ""
done

echo "🔍 VERIFICANDO ARCHIVOS ADICIONALES:"
echo "-----------------------------------"

# Otros archivos importantes
OTHER_FILES=(
    "package-lock.json"
    "requirements.txt"
    ".gitignore"
)

for FILE in "${OTHER_FILES[@]}"; do
    if [ -f "$FILE" ]; then
        SIZE=$(stat -c%s "$FILE")
        echo "✅ $FILE - Tamaño: $SIZE bytes"
    else
        echo "⚠️  $FILE - No encontrado (opcional)"
    fi
done

echo ""
echo "🌐 VERIFICANDO CONTENIDO CRÍTICO:"
echo "-----------------------------------"

# Verificar el puerto en server.js
echo "🔍 Puerto en server.js:"
if [ -f "server.js" ]; then
    PORT_LINE=$(grep -n "PORT.*=" server.js | head -1)
    if [ -n "$PORT_LINE" ]; then
        echo "   $PORT_LINE"
    else
        echo "   ❌ No se encontró configuración de puerto"
    fi
else
    echo "   ❌ server.js no encontrado"
fi

echo ""

# Verificar el script de start en package.json
echo "🔍 Script de start en package.json:"
if [ -f "package.json" ]; then
    START_LINE=$(grep -A 3 -B 1 '"start"' package.json)
    if [ -n "$START_LINE" ]; then
        echo "$START_LINE"
    else
        echo "   ❌ No se encontró script de start"
    fi
else
    echo "   ❌ package.json no encontrado"
fi

echo ""
echo "📊 RESUMEN:"
echo "-----------------------------------"

FOUND_CRITICAL=0
for FILE in "${CRITICAL_FILES[@]}"; do
    if [ -f "$FILE" ]; then
        ((FOUND_CRITICAL++))
    fi
done

echo "Archivos críticos encontrados: $FOUND_CRITICAL/${#CRITICAL_FILES[@]}"

if [ $FOUND_CRITICAL -eq ${#CRITICAL_FILES[@]} ]; then
    echo "🎉 ¡Todos los archivos críticos están presentes!"
    echo "✅ El proyecto debería poder desplegarse en Railway"
else
    echo "❌ Faltan archivos críticos"
    echo "⚠️  El deployment podría fallar"
fi

echo ""
echo "🚀 PRÓXIMOS PASOS:"
echo "-----------------------------------"
echo "1. Verificar el estado del deployment en Railway Dashboard"
echo "2. Revisar los logs de build en Railway"
echo "3. Confirmar que la URL del proyecto sea correcta"
echo "4. Si es necesario, triggerar un nuevo deployment"

# Verificar el estado del repositorio git
echo ""
echo "📋 ESTADO DEL REPOSITORIO:"
echo "-----------------------------------"

if [ -d ".git" ]; then
    echo "✅ Repositorio git detectado"
    
    # Verificar el remoto
    REMOTE=$(git remote -v 2>/dev/null | grep origin | head -1)
    if [ -n "$REMOTE" ]; then
        echo "✅ Remoto configurado: $REMOTE"
    else
        echo "⚠️  No se pudo verificar el remoto"
    fi
    
    # Verificar el último commit
    LAST_COMMIT=$(git log --oneline -1 2>/dev/null)
    if [ -n "$LAST_COMMIT" ]; then
        echo "✅ Último commit: $LAST_COMMIT"
    else
        echo "⚠️  No se pudo verificar el último commit"
    fi
else
    echo "❌ No es un repositorio git"
fi
