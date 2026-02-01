from pymongo import MongoClient
from typing import List
from datetime import datetime
import os
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
    
    # Inserts securely into the cloud
    collection.insert_one(entry)
    print("✅ Training data saved to MongoDB Atlas")