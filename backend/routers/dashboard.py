from fastapi import APIRouter, Depends
from database import get_db
from auth import get_current_user
import aiosqlite

router = APIRouter()

@router.get("/stats")
async def get_stats(
    current_user=Depends(get_current_user),
    db: aiosqlite.Connection = Depends(get_db)
):
    user_id = current_user["id"]

    # Latest analysis score
    async with db.execute(
        "SELECT overall_score, job_role FROM analyses WHERE user_id = ? ORDER BY created_at DESC LIMIT 1",
        (user_id,)
    ) as cur:
        latest = await cur.fetchone()

    # Total analyses done
    async with db.execute(
        "SELECT COUNT(*) as count FROM analyses WHERE user_id = ?", (user_id,)
    ) as cur:
        total_analyses = (await cur.fetchone())["count"]

    # Tasks completed
    async with db.execute(
        "SELECT COUNT(*) as count FROM roadmap_tasks WHERE user_id = ? AND is_completed = 1", (user_id,)
    ) as cur:
        tasks_done = (await cur.fetchone())["count"]

    # Total tasks
    async with db.execute(
        "SELECT COUNT(*) as count FROM roadmap_tasks WHERE user_id = ?", (user_id,)
    ) as cur:
        total_tasks = (await cur.fetchone())["count"]

    # Analysis history for the table
    async with db.execute(
        "SELECT id, job_role, overall_score, created_at FROM analyses WHERE user_id = ? ORDER BY created_at DESC LIMIT 10",
        (user_id,)
    ) as cur:
        history = [dict(r) for r in await cur.fetchall()]

    return {
        "overall_score": latest["overall_score"] if latest else 0,
        "current_role": latest["job_role"] if latest else "No analysis yet",
        "total_analyses": total_analyses,
        "tasks_completed": tasks_done,
        "total_tasks": total_tasks,
        "progress_percent": round((tasks_done / total_tasks * 100) if total_tasks > 0 else 0),
        "history": history
    }
