from fastapi import FastAPI, Depends, HTTPException, Form
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
import os
import requests
from typing import Optional
from supabase import create_client, Client

app = FastAPI()

# Supabase initialization
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# OAuth2 Scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

@app.get("/")
async def redirect_to_docs():
    return RedirectResponse(url="/docs")

# Pydantic models
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

# Helper function to get user from token
async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        user = supabase.auth.get_user(token)
        return user.user
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")

@app.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    try:
        res = supabase.auth.sign_in_with_password({"email": form_data.username, "password": form_data.password})
        return {"access_token": res.session.access_token, "token_type": "bearer"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Login failed: {str(e)}")

@app.post("/register")
async def register(user: UserCreate):
    try:
        res = supabase.auth.sign_up({"email": user.email, "password": user.password})
        return {"message": "Registration successful! Please check your email to verify your account."}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Registration failed: {str(e)}")

@app.post("/reset-password")
async def reset_password(email: str = Form(...)):
    try:
        res = supabase.auth.reset_password_email(email)
        return {"message": "Password reset link sent to your email!"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to send reset link: {str(e)}")

@app.get("/confirm")
async def confirm(token: str):
    try:
        # Use the Supabase client to verify the token
        res = supabase.auth.verify_otp({"token": token, "type": "email"})
        return {"message": "Email confirmed successfully! You can now log in."}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Confirmation failed: {str(e)}")
    
@app.post("/logout")
async def logout(token: str = Depends(oauth2_scheme)):
    try:
        supabase.auth.sign_out(token)
        return {"message": "Logged out successfully!"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Logout failed: {str(e)}")

@app.get("/profile", response_model=User)
async def read_profile(current_user: dict = Depends(get_current_user)):
    try:
        response = supabase.table("profiles").select("*").eq("user_id", current_user.id).execute()
        if not response.data:
            raise HTTPException(status_code=404, detail="Profile not found")
        profile = response.data[0]
        return User(**profile)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to fetch profile: {str(e)}")

@app.put("/settings", response_model=User)
async def update_settings(settings: Settings, current_user: dict = Depends(get_current_user)):
    try:
        response = supabase.table("profiles").update(settings.dict(exclude_unset=True)).eq("user_id", current_user.id).execute()
        if not response.data:
            raise HTTPException(status_code=404, detail="Profile not found")
        updated_profile = response.data[0]
        return User(**updated_profile)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to update settings: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)