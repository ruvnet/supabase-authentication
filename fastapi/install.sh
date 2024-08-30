#!/bin/bash

# Create project structure
mkdir -p app/api app/models app/db app/services

# Create main.py
cat << EOF > app/main.py
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from app.api import auth, profile

app = FastAPI()

@app.get("/")
async def redirect_to_docs():
    return RedirectResponse(url="/docs")

app.include_router(auth.router)
app.include_router(profile.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
EOF

# Create api/auth.py
cat << EOF > app/api/auth.py
from fastapi import APIRouter, Depends, HTTPException, Form
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from app.db.supabase import supabase
from app.models.user import UserCreate, User

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        user = supabase.auth.get_user(token)
        return user.user
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")

@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    try:
        res = supabase.auth.sign_in_with_password({"email": form_data.username, "password": form_data.password})
        return {"access_token": res.session.access_token, "token_type": "bearer"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Login failed: {str(e)}")

@router.post("/register")
async def register(user: UserCreate):
    try:
        res = supabase.auth.sign_up({"email": user.email, "password": user.password})
        return {"message": "Registration successful! Please check your email to verify your account."}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Registration failed: {str(e)}")

@router.post("/reset-password")
async def reset_password(email: str = Form(...)):
    try:
        res = supabase.auth.reset_password_email(email)
        return {"message": "Password reset link sent to your email!"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to send reset link: {str(e)}")

@router.get("/confirm")
async def confirm(token: str):
    try:
        res = supabase.auth.verify_otp({"token": token, "type": "email"})
        return {"message": "Email confirmed successfully! You can now log in."}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Confirmation failed: {str(e)}")

@router.post("/logout")
async def logout(token: str = Depends(oauth2_scheme)):
    try:
        supabase.auth.sign_out(token)
        return {"message": "Logged out successfully!"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Logout failed: {str(e)}")
EOF

# Create api/profile.py
cat << EOF > app/api/profile.py
from fastapi import APIRouter, Depends, HTTPException
from app.models.user import User, Settings
from app.api.auth import get_current_user
from app.db.supabase import supabase
from app.services.llama_index import get_user_index

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

@router.post("/index")
async def create_user_index(current_user: dict = Depends(get_current_user)):
    try:
        index = get_user_index(current_user.id)
        return {"message": "User index created successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to create user index: {str(e)}")
EOF

# Create models/user.py
cat << EOF > app/models/user.py
from pydantic import BaseModel
from typing import Optional

class User(BaseModel):
    id: str
    email: str
    full_name: Optional[str] = None
    bio: Optional[str] = None
    age: Optional[int] = None
    theme: Optional[str] = "light"
    notifications: Optional[bool] = True
    language: Optional[str] = "en"

class Settings(BaseModel):
    full_name: Optional[str] = None
    bio: Optional[str] = None
    age: Optional[int] = None
    theme: Optional[str] = "light"
    notifications: Optional[bool] = True
    language: Optional[str] = "en"

class UserCreate(BaseModel):
    email: str
    password: str
EOF

# Create db/supabase.py
cat << EOF > app/db/supabase.py
import os
from supabase import create_client, Client

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
EOF

# Create services/llama_index.py
cat << EOF > app/services/llama_index.py
from llama_index.vector_stores.supabase import SupabaseVectorStore
from llama_index import VectorStoreIndex, StorageContext
from app.db.supabase import supabase

def get_user_index(user_id: str):
    vector_store = SupabaseVectorStore(
        postgres_connection_string=f"{supabase.postgrest.url}?apikey={supabase.supabase_key}",
        collection_name=f"user_index_{user_id}"
    )
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    return VectorStoreIndex([], storage_context=storage_context)
EOF

# Create SQL file
cat << EOF > supabase_setup.sql
-- Enable the pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create the profiles table
CREATE TABLE IF NOT EXISTS profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id),
    full_name TEXT,
    bio TEXT,
    age INT,
    theme TEXT DEFAULT 'light',
    notifications BOOLEAN DEFAULT true,
    language TEXT DEFAULT 'en'
);

-- Create a function to handle new user signups
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS \$\$
BEGIN
    INSERT INTO public.profiles (id)
    VALUES (NEW.id);
    RETURN NEW;
END;
\$\$ LANGUAGE plpgsql SECURITY DEFINER;

-- Create a trigger to call the function on new user signups
CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();

-- Create a table for storing user-specific vector indexes
CREATE TABLE IF NOT EXISTS user_indexes (
    id UUID PRIMARY KEY REFERENCES auth.users(id),
    index_name TEXT NOT NULL,
    embedding VECTOR(1536)
);

-- Create an index on the embedding column for faster similarity searches
CREATE INDEX ON user_indexes USING ivfflat (embedding vector_cosine_ops);
EOF

echo "Project structure and files created successfully!"
echo "Don't forget to set the SUPABASE_URL and SUPABASE_KEY environment variables before running the application."
echo "Execute the SQL in supabase_setup.sql in your Supabase project to set up the necessary tables and extensions."