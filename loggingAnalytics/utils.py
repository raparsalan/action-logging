from pymongo import MongoClient
from django.conf import settings

# --- Daftar ID User (Pastikan ID di sini adalah STRING) ---
OLD_USER_IDS = ["12", "14", "15", "16", "17", "19", "20", "22", "23", "24", "25"] 
NEW_USER_IDS = ["26", "27", "28", "29", "30", "31", "32", "33", "34", "36", "13", "18"] 
PAGE_ACTIONS = [
    'home_page', 'schedule_page', 'rules_page', 'flow_page', 'sc_page',
    'parkinglot_page', 'volley_page', 'booking_page'
]

def get_user_category(user_id):
    """
    Menentukan kategori user (baru/lama) berdasarkan ID.
    MODIFIED: Memastikan user_id adalah string untuk perbandingan.
    """
    user_id_str = str(user_id) # <--- Perbaikan: Konversi ke string
    if user_id_str in NEW_USER_IDS:
        return 'new_user'
    elif user_id_str in OLD_USER_IDS: 
        return 'old_user'
    return 'unknown_user'

def get_mongo_collection():
    db_config = settings.DATABASES['default']
    
    mongo_uri = db_config['CLIENT']['host']
    db_name = db_config['NAME']
    collection_name = 'actionLogging_actionlog' 
    
    client = MongoClient(mongo_uri)
    db = client[db_name]
    return db[collection_name], client