import os
import logging
from fastapi import APIRouter, Depends, HTTPException
from app.models.user import User, Settings
from app.api.auth import get_current_user
from app.db.supabase import supabase
from app.services.llama_index import get_user_index, query_user_index

router = APIRouter()

@router.get("/profile", response_model=User)
async def read_profile(current_user: dict = Depends(get_current_user)):
    try:
        response = supabase.table("profiles").select("*").eq("user_id", current_user.id).execute()
        if not response.data:
            raise HTTPException(status_code=404, detail="Profile not found")
        profile = response.data[0]
        return User(**profile)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to fetch profile: {str(e)}")

@router.put("/settings", response_model=User)
async def update_settings(settings: Settings, current_user: dict = Depends(get_current_user)):
    try:
        response = supabase.table("profiles").update(settings.dict(exclude_unset=True)).eq("user_id", current_user.id).execute()
        if not response.data:
            raise HTTPException(status_code=404, detail="Profile not found")
        updated_profile = response.data[0]
        return User(**updated_profile)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to update settings: {str(e)}")


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@router.post("/index")
async def create_user_index(current_user: User = Depends(get_current_user)):
    try:
        logger.info(f"Attempting to create index for user: {current_user.id}")
        logger.debug(f"SUPABASE_URL set: {'SUPABASE_URL' in os.environ}")
        logger.debug(f"OPENAI_API_KEY set: {'OPENAI_API_KEY' in os.environ}")
        
        index = get_user_index(current_user.id)
        logger.info(f"Index created successfully for user: {current_user.id}")
        return {"message": "User index created successfully", "user_id": current_user.id}
    except Exception as e:
        logger.exception(f"Failed to create user index for user {current_user.id}")
        raise HTTPException(status_code=500, detail=f"Failed to create user index: {str(e)}")