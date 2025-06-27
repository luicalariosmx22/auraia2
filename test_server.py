#!/usr/bin/env python3
"""
Servidor de desarrollo simple para testing de endpoints
"""
from flask import Flask, jsonify, request
from supabase import create_client
from dotenv import load_dotenv
import os

# Cargar variables de entorno
load_dotenv()

app = Flask(__name__)

# Configurar Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

@app.route('/test/ping')
def ping():
    return jsonify({"status": "ok", "message": "Server is running"})

@app.route('/test/<nombre_nora>/bloques')
def test_listar_bloques(nombre_nora):
    """Test: Listar bloques de conocimiento"""
    try:
        print(f"🔍 TEST - Buscando bloques para: {nombre_nora}")
        res = supabase.table("conocimiento_nora").select("*").eq("nombre_nora", nombre_nora).eq("activo", True).order("fecha_creacion", desc=True).execute()
        print(f"✅ TEST - Resultado: {len(res.data)} bloques")
        return jsonify({
            "success": True, 
            "data": res.data, 
            "test": True,
            "total": len(res.data)
        })
    except Exception as e:
        print(f"❌ TEST - Error: {str(e)}")
        return jsonify({
            "success": False, 
            "message": str(e), 
            "test": True
        }), 500

@app.route('/test/<nombre_nora>/crear-datos', methods=['POST'])
def test_crear_datos_prueba(nombre_nora):
    """Test: Crear datos de prueba"""
    try:
        datos_prueba = [
            {
                "nombre_nora": nombre_nora,
                "contenido": "Somos una empresa de marketing digital especializada en automatización con IA. Ofrecemos servicios de chatbots, análisis de datos y estrategias de contenido.",
                "etiquetas": ["servicios", "marketing", "ia"],
                "origen": "manual",
                "prioridad": True,
                "activo": True
            },
            {
                "nombre_nora": nombre_nora,
                "contenido": "Nuestro horario de atención es de lunes a viernes de 9:00 AM a 6:00 PM. Los fines de semana respondemos emergencias por WhatsApp.",
                "etiquetas": ["horarios", "contacto", "atencion"],
                "origen": "manual",
                "prioridad": False,
                "activo": True
            },
            {
                "nombre_nora": nombre_nora,
                "contenido": "Ofrecemos planes desde $99/mes para pequeñas empresas hasta $999/mes para corporativos. Incluye chatbot, análisis mensual y soporte técnico.",
                "etiquetas": ["precios", "planes", "costos"],
                "origen": "manual",
                "prioridad": True,
                "activo": True
            }
        ]
        
        res = supabase.table("conocimiento_nora").insert(datos_prueba).execute()
        print(f"✅ TEST - Creados {len(res.data)} bloques de prueba")
        return jsonify({
            "success": True, 
            "data": res.data, 
            "test": True,
            "created": len(res.data)
        })
    except Exception as e:
        print(f"❌ TEST - Error creando datos: {str(e)}")
        return jsonify({
            "success": False, 
            "message": str(e), 
            "test": True
        }), 500

if __name__ == '__main__':
    print("🚀 Iniciando servidor de test en puerto 8000...")
    app.run(debug=True, port=8000)
