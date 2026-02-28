import os
from typing import List
from datetime import datetime
from pymongo import MongoClient
from core.config import config

client = MongoClient(config.MONGODB_URL)
db = client[config.MONGODB_AGENT]
collection = db[config.MONGODB_LOGS]

def log_training_data(history: List[str], chosen_reply: List[str], metadata):
    entry = {
        "timestamp": datetime.now(),
        "chat_history": history,
        "chosen_reply": chosen_reply,
        "metadata": metadata,
    }
    
    collection.insert_one(entry)