from motor.motor_asyncio import AsyncIOMotorClient
from fastapi import HTTPException
from .utils import json_serial, clean_data
import logging
import os


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MONGO_DETAILS = os.getenv("MONGO_DETAILS", "mongodb+srv://zzcv00:dwiqPBh62FHd1sLb@coffee.ntxtbdl.mongodb.net/?retryWrites=true&w=majority&appName=coffee")
client = AsyncIOMotorClient(MONGO_DETAILS)
database = client['lkj']
collection = database['JBTI']

# MongoDB 연결 테스트
async def connect_to_mongo():
    try:
        await client.admin.command('ping')
        logger.info("Successfully connected to MongoDB")
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {e}")

async def fetch_job_fields():
    try:
        projection = {"직무": 1, "직종": 1, "_id": 0}
        cursor = collection.find({}, projection)
        results = await cursor.to_list(length=None)
        return clean_data(results)
    except Exception as e:
        logger.error(f"Error fetching job fields: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch job fields")

async def fetch_job_details():
    try:
        projection = {"직종": 1, "직업 설명": 1, "수행 직무": 1, "필요기술 및 지식": 1, "직업 전망": 1, "_id": 0}
        cursor = collection.find({}, projection)
        results = await cursor.to_list(length=None)
        return clean_data(results)
    except Exception as e:
        logger.error(f"Error fetching job details: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch job details")
