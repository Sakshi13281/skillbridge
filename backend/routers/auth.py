from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr
from database import get_db
from auth import hash_password, verify_password, create_token, get_current_user
import aiosqlite

router = APIRouter()

class RegisterInput(BaseModel):
    name: str
    email: str
    password: str

class LoginInput(BaseModel):
    email: str
    password: str

@router.post("/register")
async def register(data: RegisterInput, db: aiosqlite.Connection = Depends(get_db)):
    # Check if email already exists
    async with db.execute("SELECT id FROM users WHERE email = ?", (data.email,)) as cur:
        existing = await cur.fetchone()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed = hash_password(data.password)
    async with db.execute(
        "INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
        (data.name, data.email, hashed)
    ) as cur:
        user_id = cur.lastrowid
    await db.commit()

    token = create_token(user_id, data.email)
    return {"token": token, "name": data.name, "email": data.email}

@router.post("/login")
async def login(data: LoginInput, db: aiosqlite.Connection = Depends(get_db)):
    async with db.execute("SELECT * FROM users WHERE email = ?", (data.email,)) as cur:
        user = await cur.fetchone()

    if not user or not verify_password(data.password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = create_token(user["id"], user["email"])
    return {"token": token, "name": user["name"], "email": user["email"]}

@router.get("/me")
async def me(current_user=Depends(get_current_user), db: aiosqlite.Connection = Depends(get_db)):
    async with db.execute("SELECT id, name, email, bio FROM users WHERE id = ?", (current_user["id"],)) as cur:
        user = await cur.fetchone()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return dict(user)
