import json
import logging
from typing import List
from datetime import datetime
from core.config import config
from config.db import mongodb_db
from pymongo.errors import ServerSelectionTimeoutError, AutoReconnect

FAILED_LOGS_KEY = "logs:failed_training_data"

collection = mongodb_db[config.MONGODB_LOGS]

central_logger = logging.getLogger(config.CENTRAL_LOGGER_NAME)

def log_training_data(history: List[str], chosen_reply: List[str], metadata: dict, redis_client):
    entry = {
        "timestamp": datetime.now(),
        "chat_history": history,
        "chosen_reply": chosen_reply,
        "metadata": metadata,
    }
    
    try:
        collection.insert_one(entry)
        
    except (ServerSelectionTimeoutError, AutoReconnect) as e:
        central_logger.error("MongoDB failed: {%s}. Saving to Redis fallback.", e)
        try:
            redis_client.lpush(FAILED_LOGS_KEY, json.dumps(entry))
        except Exception as redis_e:
            central_logger.critical("Both Mongo and Redis failed to log data: %s. Exception: %s", entry, redis_e)