#!/bin/bash
# Script para verificar estado de Railway deployment

echo "🔍 VERIFICACIÓN DE DEPLOYMENT RAILWAY"
echo "======================================"

echo ""
echo "📁 Archivos de configuración presentes:"
if [ -f "Procfile" ]; then
    echo "✅ Procfile existe"
    echo "   Contenido: $(cat Procfile)"
else
    echo "❌ Procfile falta"
fi

if [ -f "railway.json" ]; then
    echo "✅ railway.json existe"
    echo "   Contenido: $(cat railway.json)"
else
    echo "❌ railway.json falta"
fi

if [ -f "requirements.txt" ]; then
    echo "✅ requirements.txt existe"
    echo "   Líneas: $(wc -l < requirements.txt)"
    if grep -q "gunicorn" requirements.txt; then
        echo "   ✅ gunicorn está incluido"
    else
        echo "   ❌ gunicorn no está incluido"
    fi
else
    echo "❌ requirements.txt falta"
fi

echo ""
echo "📊 Estado del repositorio Git:"
git status --porcelain
echo ""
echo "🔄 Último commit:"
git log --oneline -1

echo ""
echo "🚀 Para activar deployment en Railway:"
echo "1. Ve a https://railway.app/dashboard"
echo "2. Encuentra tu proyecto"
echo "3. Ve a Settings → Environment"
echo "4. Asegúrate de tener estas variables:"
echo "   - PORT (Railway lo asigna automáticamente)"
echo "   - SECRET_KEY (tu clave secreta Flask)"
echo "   - SUPABASE_URL (tu URL de Supabase)"
echo "   - SUPABASE_KEY (tu clave de Supabase)"
echo "   - OPENAI_API_KEY (tu clave de OpenAI)"
echo "5. Ve a Deployments y haz clic en 'Redeploy' si es necesario"
