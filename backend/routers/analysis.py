from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Dict
from database import get_db
from auth import get_current_user
from ai_client import ask_ai_json
import aiosqlite
import json

router = APIRouter()

class AnalysisInput(BaseModel):
    job_role: str
    skill_ratings: Dict[str, int]  # e.g. {"Python": 6, "SQL": 3}


def build_analysis_prompt(job_role, skills_text, avg_rating, strong_skills, weak_skills):
    """
    The prompt is in its own function so it is easy to find and edit.
    Change any plain English text freely.
    The {placeholders} are filled in by Python before sending to Gemini.
    """
    strong = ", ".join(strong_skills) if strong_skills else "none yet"
    weak   = ", ".join(weak_skills)   if weak_skills   else "none"

    return f"""
You are an experienced tech hiring manager and career coach with 10+ years of experience
hiring for {job_role} positions at startups and mid-size tech companies.

A candidate is self-assessing their skills for a {job_role} role (entry to mid level).
They rated themselves out of 10 — where 0 = no knowledge, 10 = expert level.

Their self-rated skills:
{skills_text}

Quick stats:
- Average rating: {avg_rating:.1f}/10
- Strong skills (7+): {strong}
- Weak skills (4 or below): {weak}

=== PART 1 — SKILL GAP ANALYSIS ===

Analyse each skill honestly. Rules:
- This is ENTRY TO MID LEVEL — not a senior role. Be realistic but fair.
- If someone rates a skill 7+ and the requirement is also 7, gap = 0 (they are ready).
- overall_score: 40-55 = needs significant work, 56-70 = getting there, 71-85 = nearly ready, 86+ = strong candidate.

FOR RESOURCES — only use these real trusted URLs (replace SKILL with the actual skill name):
- YouTube search: https://www.youtube.com/results?search_query=SKILL+tutorial
- freeCodeCamp: https://www.freecodecamp.org/learn
- W3Schools SQL: https://www.w3schools.com/sql/
- W3Schools Python: https://www.w3schools.com/python/
- W3Schools JS: https://www.w3schools.com/js/
- MDN Web Docs: https://developer.mozilla.org/en-US/docs/Learn
- Kaggle free courses: https://www.kaggle.com/learn
- Python docs: https://docs.python.org/3/tutorial/
- React docs: https://react.dev/learn
- Git docs: https://git-scm.com/doc
- CS50 Harvard (free): https://cs50.harvard.edu/x/

=== PART 2 — JOB HIRING PREDICTION ===

Based on the SAME skill ratings above, predict this candidate's realistic chance
of getting hired as a {job_role} if they started applying to jobs TODAY.

Think about:
- Do they meet the minimum bar that most job postings require?
- How competitive is the {job_role} job market?
- Which of their skills would impress a recruiter on a CV?
- Which gaps would cause most recruiters to reject them at the screening stage?
- What single improvement would most increase their hiring chances?

Hiring chance label rules:
- 0-25%   = "Low"      — significant gaps in core skills, not ready yet
- 26-50%  = "Moderate" — some good skills but missing key requirements
- 51-75%  = "Good"     — competitive candidate with only minor gaps
- 76-100% = "Strong"   — ready to apply, very likely to get interviews

=== RETURN FORMAT ===

Return ONLY a valid JSON object — no extra text, no markdown, no code fences:
{{
  "overall_score": <integer 0-100, overall readiness score>,
  "summary": "<3 sentences: 1 — what they are good at, 2 — their biggest gap, 3 — the single most important action to take now>",
  "skills": [
    {{
      "name": "<exact skill name as user provided>",
      "user_level": <their self-rating as integer>,
      "required_level": <realistic entry-mid {job_role} requirement 0-10>,
      "gap": <required_level minus user_level, negative means they exceed requirement>,
      "priority": "<high if gap >= 3 | medium if gap 1-2 | low if gap <= 0>",
      "why_it_matters": "<one specific sentence: how this skill is actually used daily in a {job_role} job>",
      "top_resource": {{
        "title": "<resource name>",
        "url": "<real URL from the trusted list above>",
        "type": "<course | video | documentation | practice>"
      }}
    }}
  ],
  "job_prediction": {{
    "hiring_chance": <integer 0-100, realistic chance of getting hired right now>,
    "confidence_label": "<Low | Moderate | Good | Strong>",
    "strengths": [
      "<specific strength 1 that would impress a recruiter>",
      "<specific strength 2>",
      "<specific strength 3 — only add if genuinely strong, otherwise use 2>"
    ],
    "blockers": [
      "<specific blocker 1 that would cause rejection at most companies>",
      "<specific blocker 2 — only include real blockers, not minor issues>"
    ],
    "biggest_boost": "<one very concrete action that would most increase hiring chances>",
    "market_insight": "<one sentence about the current {job_role} job market — demand, competition, what employers prioritise>"
  }}
}}
"""


@router.post("/run")
async def run_analysis(
    data: AnalysisInput,
    current_user=Depends(get_current_user),
    db: aiosqlite.Connection = Depends(get_db)
):
    skills_text   = "\n".join([f"- {skill}: {rating}/10" for skill, rating in data.skill_ratings.items()])
    total_skills  = len(data.skill_ratings)
    avg_rating    = sum(data.skill_ratings.values()) / total_skills if total_skills > 0 else 0
    strong_skills = [s for s, r in data.skill_ratings.items() if r >= 7]
    weak_skills   = [s for s, r in data.skill_ratings.items() if r <= 4]

    prompt = build_analysis_prompt(
        data.job_role, skills_text, avg_rating, strong_skills, weak_skills
    )

    try:
        result = await ask_ai_json(prompt)
    except Exception as e:
        
        raise HTTPException(status_code=500, detail=f"AI analysis failed: {str(e)}")

    # Save both skills and job_prediction together in one database column
    skill_data_to_save = {
        "skills":         result.get("skills", []),
        "job_prediction": result.get("job_prediction", {})
    }

    async with db.execute(
        """INSERT INTO analyses (user_id, job_role, overall_score, skill_data, ai_summary)
           VALUES (?, ?, ?, ?, ?)""",
        (
            current_user["id"],
            data.job_role,
            result.get("overall_score", 0),
            json.dumps(skill_data_to_save),
            result.get("summary", "")
        )
    ) as cur:
        analysis_id = cur.lastrowid
    await db.commit()

    return {
        "analysis_id":    analysis_id,
        "job_role":       data.job_role,
        "overall_score":  result.get("overall_score", 0),
        "summary":        result.get("summary", ""),
        "skills":         result.get("skills", []),
        "job_prediction": result.get("job_prediction", {})
    }


@router.get("/latest")
async def get_latest_analysis(
    current_user=Depends(get_current_user),
    db: aiosqlite.Connection = Depends(get_db)
):
    async with db.execute(
        "SELECT * FROM analyses WHERE user_id = ? ORDER BY created_at DESC LIMIT 1",
        (current_user["id"],)
    ) as cur:
        row = await cur.fetchone()

    if not row:
        raise HTTPException(status_code=404, detail="No analysis found. Please run an analysis first.")

    saved = json.loads(row["skill_data"])

    # Handle both old format (plain list) and new format (dict with skills + prediction)
    if isinstance(saved, list):
        skills         = saved
        job_prediction = {}
    else:
        skills         = saved.get("skills", [])
        job_prediction = saved.get("job_prediction", {})

    return {
        "analysis_id":    row["id"],
        "job_role":       row["job_role"],
        "overall_score":  row["overall_score"],
        "summary":        row["ai_summary"],
        "skills":         skills,
        "job_prediction": job_prediction
    }


@router.get("/history")
async def get_history(
    current_user=Depends(get_current_user),
    db: aiosqlite.Connection = Depends(get_db)
):
    async with db.execute(
        "SELECT id, job_role, overall_score, created_at FROM analyses WHERE user_id = ? ORDER BY created_at DESC",
        (current_user["id"],)
    ) as cur:
        rows = await cur.fetchall()
    return [dict(r) for r in rows]
