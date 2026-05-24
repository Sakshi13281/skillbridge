from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from database import get_db
from auth import get_current_user
from ai_client import ask_ai_json
import aiosqlite
import json

router = APIRouter()

class RoadmapInput(BaseModel):
    analysis_id: int
    job_role: str
    skills: list  # the skills array from the analysis result

@router.post("/generate")
async def generate_roadmap(
    data: RoadmapInput,
    current_user=Depends(get_current_user),
    db: aiosqlite.Connection = Depends(get_db)
):
    """
    Takes the skill gap analysis and asks Gemini to create
    a realistic week-by-week learning plan to close those gaps.
    """

    # Only include skills where there's actually a gap to close
    gaps = [s for s in data.skills if s.get("gap", 0) > 0]

    if not gaps:
        raise HTTPException(status_code=400, detail="No skill gaps found to build a roadmap from.")

    # Sort by priority so Gemini focuses on the important ones
    priority_order = {"high": 0, "medium": 1, "low": 2}
    gaps.sort(key=lambda x: priority_order.get(x.get("priority", "low"), 2))

    gaps_text = "\n".join([
        f"- {s['name']}: currently {s['user_level']}/10, needs {s['required_level']}/10 (gap: {s['gap']}, priority: {s['priority']})"
        for s in gaps
    ])

    # Calculate realistic number of weeks based on number of gaps
    # More gaps = more weeks needed, but cap at 8
    num_weeks = min(max(len(gaps), 3), 8)

    # Separate skills by priority for the prompt context
    high_priority  = [s["name"] for s in gaps if s.get("priority") == "high"]
    medium_priority = [s["name"] for s in gaps if s.get("priority") == "medium"]
    low_priority   = [s["name"] for s in gaps if s.get("priority") == "low"]

    prompt = f"""
You are a professional career coach who specialises in helping people break into tech roles.
You are creating a personalised learning roadmap for someone who wants to become a {data.job_role}.

Their current skill gaps (sorted by priority — tackle these in order):
{gaps_text}

Priority breakdown:
- HIGH priority skills (biggest gaps, tackle first): {", ".join(high_priority) if high_priority else "none"}
- MEDIUM priority (important but smaller gaps): {", ".join(medium_priority) if medium_priority else "none"}
- LOW priority (minor gaps or nearly ready): {", ".join(low_priority) if low_priority else "none"}

CREATE A {num_weeks}-WEEK LEARNING ROADMAP following these rules:

RULE 1 — Week structure:
- Weeks 1-{max(1, num_weeks//2)}: Focus ONLY on high priority skills. Build foundations first.
- Weeks {max(2, num_weeks//2 + 1)}-{num_weeks}: Move to medium and low priority skills.
- Each week has a clear single theme (e.g. "SQL Foundations" or "Python for Data")

RULE 2 — Task rules:
- Each week must have exactly 2 to 3 tasks
- Each task must be SPECIFIC and ACTIONABLE — not vague like "learn Python"
- Good example: "Complete the SQL SELECT, WHERE and JOIN chapters on W3Schools and write 10 practice queries"
- Each task should take 2-3 hours so the whole week is 5-8 hours total (part-time learner)

RULE 3 — Resources — VERY IMPORTANT:
Only use URLs from this trusted list. Replace SKILL with the actual skill name:
- YouTube search: https://www.youtube.com/results?search_query=SKILL+for+beginners
- freeCodeCamp: https://www.freecodecamp.org/learn
- W3Schools SQL: https://www.w3schools.com/sql/
- W3Schools Python: https://www.w3schools.com/python/
- W3Schools JavaScript: https://www.w3schools.com/js/
- MDN Web Docs: https://developer.mozilla.org/en-US/docs/Learn
- Kaggle free courses: https://www.kaggle.com/learn
- Python official tutorial: https://docs.python.org/3/tutorial/
- React official docs: https://react.dev/learn
- Git official docs: https://git-scm.com/doc
- CS50 (free Harvard course): https://cs50.harvard.edu/x/
- Google Data Analytics (Coursera): https://www.coursera.org/professional-certificates/google-data-analytics
Do NOT invent URLs. If unsure, use the YouTube search URL for that skill.

Return ONLY a valid JSON object — no extra text, no markdown:
{{
  "weeks": [
    {{
      "week_number": 1,
      "theme": "<short punchy theme e.g. 'SQL Foundations' or 'Python Basics'>",
      "tasks": [
        {{
          "skill_name": "<which skill from the gap list this covers>",
          "title": "<short specific task title — max 8 words>",
          "description": "<exactly what to do — be specific, mention chapters, exercises or projects>",
          "estimated_hours": <2 or 3>,
          "resource_url": "<real URL from the trusted list above>",
          "resource_type": "<course | video | documentation | practice>"
        }}
      ]
    }}
  ]
}}
"""

    try:
        result = await ask_ai_json(prompt)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI roadmap generation failed: {str(e)}")

    # Delete any old roadmap tasks for this analysis
    await db.execute(
        "DELETE FROM roadmap_tasks WHERE user_id = ? AND analysis_id = ?",
        (current_user["id"], data.analysis_id)
    )

    # Save all tasks to the database
    for week in result.get("weeks", []):
        for task in week.get("tasks", []):
            await db.execute(
                """INSERT INTO roadmap_tasks
                   (user_id, analysis_id, week_number, skill_name, task_title, task_description, resource_url, resource_type)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    current_user["id"],
                    data.analysis_id,
                    week["week_number"],
                    task.get("skill_name", ""),
                    task.get("title", ""),
                    task.get("description", ""),
                    task.get("resource_url", ""),
                    task.get("resource_type", "article")
                )
            )
    await db.commit()

    return {"weeks": result.get("weeks", []), "analysis_id": data.analysis_id}

@router.get("/latest")
async def get_latest_roadmap(
    current_user=Depends(get_current_user),
    db: aiosqlite.Connection = Depends(get_db)
):
    # Get the most recent analysis id for this user
    async with db.execute(
        "SELECT id FROM analyses WHERE user_id = ? ORDER BY created_at DESC LIMIT 1",
        (current_user["id"],)
    ) as cur:
        analysis = await cur.fetchone()

    if not analysis:
        raise HTTPException(status_code=404, detail="No roadmap found. Please run an analysis first.")

    analysis_id = analysis["id"]

    async with db.execute(
        """SELECT * FROM roadmap_tasks
           WHERE user_id = ? AND analysis_id = ?
           ORDER BY week_number, id""",
        (current_user["id"], analysis_id)
    ) as cur:
        tasks = await cur.fetchall()

    if not tasks:
        raise HTTPException(status_code=404, detail="No roadmap tasks found. Please generate a roadmap first.")

    # Group tasks by week
    weeks = {}
    for task in tasks:
        w = task["week_number"]
        if w not in weeks:
            weeks[w] = {"week_number": w, "tasks": []}
        weeks[w]["tasks"].append({
            "id": task["id"],
            "skill_name": task["skill_name"],
            "title": task["task_title"],
            "description": task["task_description"],
            "resource_url": task["resource_url"],
            "resource_type": task["resource_type"],
            "is_completed": bool(task["is_completed"])
        })

    return {"weeks": list(weeks.values()), "analysis_id": analysis_id}

@router.patch("/task/{task_id}/complete")
async def toggle_task(
    task_id: int,
    current_user=Depends(get_current_user),
    db: aiosqlite.Connection = Depends(get_db)
):
    async with db.execute(
        "SELECT is_completed FROM roadmap_tasks WHERE id = ? AND user_id = ?",
        (task_id, current_user["id"])
    ) as cur:
        task = await cur.fetchone()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    new_status = 0 if task["is_completed"] else 1
    await db.execute(
        "UPDATE roadmap_tasks SET is_completed = ? WHERE id = ?",
        (new_status, task_id)
    )
    await db.commit()
    return {"task_id": task_id, "is_completed": bool(new_status)}
