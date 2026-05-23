from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from database import get_db
from auth import get_current_user
import aiosqlite

router = APIRouter()

class ProfileUpdate(BaseModel):
    name: str
    bio: str

@router.get("/")
async def get_profile(
    current_user=Depends(get_current_user),
    db: aiosqlite.Connection = Depends(get_db)
):
    async with db.execute(
        "SELECT id, name, email, bio, created_at FROM users WHERE id = ?",
        (current_user["id"],)
    ) as cur:
        user = await cur.fetchone()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return dict(user)

@router.put("/update")
async def update_profile(
    data: ProfileUpdate,
    current_user=Depends(get_current_user),
    db: aiosqlite.Connection = Depends(get_db)
):
    await db.execute(
        "UPDATE users SET name = ?, bio = ? WHERE id = ?",
        (data.name, data.bio, current_user["id"])
    )
    await db.commit()
    return {"message": "Profile updated successfully"}
