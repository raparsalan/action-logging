from pymongo import MongoClient
from django.conf import settings

OLD_USER_IDS = [
    ["12", "14", "15", "16", "17", "19", "20", "22", "23", "24", "25"],
    ["37", "38", "57", "40", "41", "42", "59", "44", "45", "46","60"]
    ] 
NEW_USER_IDS = [
    ["26", "27", "28", "29", "30", "31", "32", "33", "34", "36", "13", "18"],
    ["61", "48", "49", "50", "51", "52", "53", "54", "55", "56", "62"]
    ] 

PAGE_ACTIONS = [
    'home_page', 'schedule_page', 'rules_page', 'flow_page', 'sc_page',
    'parkinglot_page', 'volley_page', 'booking_page'
]

def get_user_category(user_id,id=None):
    """
    Menentukan kategori user (baru/lama) berdasarkan ID.
    MODIFIED: Memastikan user_id adalah string untuk perbandingan.
    """
    user_id_str = str(user_id)
    if id:
        if user_id_str in NEW_USER_IDS[id-1]:
            return 'new_user'
        elif user_id_str in OLD_USER_IDS[id-1]: 
            return 'old_user'
    else:
        # merge user
        ALL_NEW_USERS = [user for sublist in NEW_USER_IDS for user in sublist]
        ALL_OLD_USERS = [user for sublist in OLD_USER_IDS for user in sublist]
        if user_id_str in ALL_NEW_USERS:
            return 'new_user'
        elif user_id_str in ALL_OLD_USERS: 
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