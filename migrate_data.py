import firebase_admin
import os
import json

from firebase_admin import credentials
from firebase_admin import firestore

# Initialize Firebase Admin SDK
def initialize_firebase_app():
    """Initializes the Firebase Admin SDK if not already initialized."""
    service_account_key_path = "./serviceAccountKey.json"
    print("Reading service account key file...")
    try:
        with open(service_account_key_path, "r", encoding="utf-8") as f:
            file_content = f.read()
            print(f"File content:\n{file_content}")
    except FileNotFoundError:
        print(f"File not found: {service_account_key_path}")
    except Exception as e:
        print(f"Error reading file: {e}")
    if not firebase_admin._apps:
        try:
            cred = credentials.Certificate(service_account_key_path)
            firebase_admin.initialize_app(cred)
            print("Firebase Admin SDK initialized successfully.")
            
            print(f"firebase_admin version: {firebase_admin.__version__}")
        except FileNotFoundError:
            print(f"Error: Service account key file not found at {service_account_key_path}")
            return None  # Indicate failure
        except Exception as e:
            print(f"Error initializing Firebase Admin SDK: {e}")
            return None  # Indicate failure
    else:
      print("Firebase Admin SDK already initialized.")

    # Get an instance of Firestore
    return firestore.client()


def migrate_nora_data(nora_name):
    """Migrates the data of a specific Nora from JSON and TXT files to Firestore."""
    nora_folder = os.path.join("clientes", nora_name)

    if not os.path.exists(nora_folder):
        print(f"Folder not found for Nora: {nora_name}")
        return

    # Create a document in the 'noras' collection
    nora_ref = firestore_db.collection("noras").document(nora_name)
    nora_data = {"name": nora_name}

    # Read config.json and upload the data
    config_file_path = os.path.join(nora_folder, "config.json")
    if os.path.exists(config_file_path):
        with open(config_file_path, "r", encoding="utf-8") as f:
            config_data = json.load(f)
            nora_data["config"] = config_data
            # Add fields that go in the root of the document
            nora_data["display_name"] = config_data.get("nombre_display")
            nora_data["ia_activated"] = config_data.get("ia_activada")
            nora_data["modules"] = config_data.get("modulos")
            nora_data["last_update"] = config_data.get("ultima_actualizacion")

    # Upload database files
    nora_data["database"] = {}
    database_files = {
        "contactos": "crm/contactos.json",
        "respuestas": "respuestas/respuestas.json",
        "envios_programados": "envios/envios_programados.json",
        "historial": "ia/historial.json",
        "categorias": "categorias.json",
        "bot_data": "bot_data.json",
    }

    for db_field, file_name in database_files.items():
        file_path = os.path.join(nora_folder, file_name)
        if os.path.exists(file_path):
            if file_name.endswith(".json"):
                with open(file_path, "r", encoding="utf-8") as f:
                    try:
                        nora_data["database"][db_field] = json.load(f)
                    except json.JSONDecodeError as e:
                        print(f"Error decoding JSON in {file_name}: {e}")
                        nora_data["database"][db_field] = {}
            elif file_name.endswith(".txt"): 
                with open(file_path, "r", encoding="utf-8") as f:
                    nora_data["database"][db_field] = f.read()

    # Add global files if exist
    global_file_path = os.path.join("clientes", nora_name, "servicios_conocimiento.txt")
    if os.path.exists(global_file_path):
      with open(global_file_path, "r") as f:
        nora_data["database"]["servicios_conocimiento"] = f.read()


    # Upload the data to Firestore
    nora_ref.set(nora_data)
    print(f"Data for Nora '{nora_name}' migrated successfully.")


def migrate_all_data():
    """Migrates the data of all Noras found in the 'clientes' folder."""
    clientes_folder = "clientes"
    if not os.path.exists(clientes_folder):
        print(f"Folder not found: {clientes_folder}")
        return

    # Iterate over the folders in the clientes folder
    for folder_name in os.listdir(clientes_folder):
        folder_path = os.path.join(clientes_folder, folder_name)

        # Check if it is a directory, and if so, migrate the data.
        if os.path.isdir(folder_path):
            migrate_nora_data(folder_name)


# Example usage:
# To migrate data for a specific Nora:
# migrate_nora_data("aura")


# Initialize Firebase
firestore_db = initialize_firebase_app()

# Migrate all data
migrate_all_data()

