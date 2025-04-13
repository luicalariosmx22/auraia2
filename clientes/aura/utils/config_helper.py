# utils/config_helper.py

import json

def cargar_configuracion():
    try:
        with open('config.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {"usar_openai": False}

def guardar_configuracion(data):
    with open('config.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
