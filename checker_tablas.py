import os
import re
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

class SupabaseTableChecker:
    def __init__(self):
        self.supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        self.verified_tables = set()
        self.results = []

    def check_table_exists(self, table_name: str) -> bool:
        if table_name in self.verified_tables:
            return True
        try:
            self.supabase.from_(table_name).select("*").limit(1).execute()
            self.verified_tables.add(table_name)
            return True
        except:
            return False

    def check_column_exists(self, table_name: str, column_name: str) -> bool:
        if not self.check_table_exists(table_name):
            return False
        try:
            self.supabase.from_(table_name).select(column_name).limit(1).execute()
            return True
        except:
            return False
