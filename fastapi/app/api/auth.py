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
