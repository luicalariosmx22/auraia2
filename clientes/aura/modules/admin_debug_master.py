import os
import json
import logging
from datetime import datetime
from clientes.aura.utils.supabase_client import supabase

def debug_master():
    try:
        logging.info("Debugging master started.")
        # Your debugging logic here
    except Exception as e:
        logging.error(f"An error occurred: {e}")