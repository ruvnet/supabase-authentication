import logging
from llama_index.core import VectorStoreIndex, StorageContext
from llama_index.vector_stores.supabase import SupabaseVectorStore
from app.db.supabase import SUPABASE_URL, SUPABASE_KEY
import os
from urllib.parse import urlparse
import asyncio
from asyncio import TimeoutError
logger = logging.getLogger(__name__)

async def get_user_index_with_timeout(user_id: str, timeout: int = 30):
    try:
        return await asyncio.wait_for(get_user_index(user_id), timeout=timeout)
    except TimeoutError:
        logger.error(f"Timeout occurred while creating index for user {user_id}")
        raise HTTPException(status_code=504, detail="Index creation timed out")
    
def get_user_index(user_id: str):
    logger.info(f"Starting get_user_index for user: {user_id}")
    
    if 'OPENAI_API_KEY' not in os.environ:
        logger.error("OPENAI_API_KEY is not set in the environment variables")
        raise ValueError("OPENAI_API_KEY is not set in the environment variables")

    try:
        parsed_url = urlparse(SUPABASE_URL)
        DB_CONNECTION = f"postgresql://{parsed_url.username}:{parsed_url.password}@{parsed_url.hostname}:{parsed_url.port or 5432}/{parsed_url.path.lstrip('/')}"
        logger.debug(f"Constructed DB_CONNECTION (sensitive info redacted): postgresql://{parsed_url.username}:****@{parsed_url.hostname}:{parsed_url.port or 5432}/{parsed_url.path.lstrip('/')}")

        logger.info("Initializing SupabaseVectorStore")
        vector_store = SupabaseVectorStore(
            postgres_connection_string=DB_CONNECTION,
            collection_name=f'user_collection_{user_id}'
        )
        
        logger.info("Creating StorageContext")
        storage_context = StorageContext.from_defaults(vector_store=vector_store)
        
        logger.info("Creating VectorStoreIndex")
        index = VectorStoreIndex.from_documents([], storage_context=storage_context)
        
        logger.info(f"Successfully created index for user: {user_id}")
        return index
    except Exception as e:
        logger.exception(f"Error in get_user_index for user {user_id}")
        raise

def query_user_index(user_id: str, query: str):
    logger.info(f"Starting query_user_index for user: {user_id}")
    try:
        index = get_user_index(user_id)
        query_engine = index.as_query_engine()
        response = query_engine.query(query)
        logger.info(f"Successfully queried index for user: {user_id}")
        return str(response)
    except Exception as e:
        logger.exception(f"Error in query_user_index for user {user_id}")
        raise