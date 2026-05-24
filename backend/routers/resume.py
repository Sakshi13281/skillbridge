from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from auth import get_current_user
from ai_client import ask_ai_json
import PyPDF2
import io

router = APIRouter()

def extract_text_from_pdf(file_bytes: bytes) -> str:
    """
    Reads a PDF file and extracts all the text from it.
    Think of it like copy-pasting all text from a PDF into a string.
    """
    try:
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() or ""
        return text.strip()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Could not read PDF: {str(e)}")


@router.post("/extract")
async def extract_skills_from_resume(
    file: UploadFile = File(...),
    job_role: str = "Software Developer",
    current_user=Depends(get_current_user)
):
    """
    Takes a PDF resume, extracts text from it, sends to Groq AI,
    and gets back a list of skills with estimated levels.
    """

    # Check it is actually a PDF
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Please upload a PDF file only.")

    # Check file size — max 5MB
    file_bytes = await file.read()
    if len(file_bytes) > 5 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File too large. Please upload a PDF under 5MB.")

    # Extract text from PDF
    resume_text = extract_text_from_pdf(file_bytes)

    if not resume_text or len(resume_text) < 50:
        raise HTTPException(status_code=400, detail="Could not extract text from this PDF. Make sure it is not a scanned image PDF.")

    # Only send first 3000 characters to avoid token limits
    resume_text = resume_text[:3000]

    # ------------------------------------------------------------------ #
    #  PROMPT — change the plain English text freely.                     #
    #  Do NOT change anything inside { } — those are Python variables.   #
    # ------------------------------------------------------------------ #
    prompt = f"""
You are an expert technical recruiter who is very good at reading resumes and identifying skill levels.

A candidate is applying for a {job_role} position. Here is their resume text:

---
{resume_text}
---

Read the resume carefully and extract their technical and professional skills.
For each skill you find, estimate their level from 0 to 10 based on:
- Years of experience mentioned
- Projects they used it in
- Certifications or education related to it
- How prominently it features in their resume

Rating guide:
- 0-2 = mentioned once, no real experience
- 3-4 = basic knowledge, used in small projects
- 5-6 = moderate experience, used in multiple projects
- 7-8 = strong experience, used professionally
- 9-10 = expert level, extensive professional experience

Focus on skills relevant to {job_role} roles. Extract between 5 and 10 most relevant skills.

Return ONLY a valid JSON object — no extra text, no markdown:
{{
  "extracted_skills": [
    {{
      "name": "<skill name>",
      "level": <estimated level 0-10>,
      "reason": "<one short sentence explaining why you gave this level>"
    }}
  ],
  "summary": "<2 sentences summarising this candidate's overall profile based on their resume>"
}}
"""

    try:
        result = await ask_ai_json(prompt)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI extraction failed: {str(e)}")

    return {
        "extracted_skills": result.get("extracted_skills", []),
        "summary": result.get("summary", ""),
        "filename": file.filename
    }

from pydantic import BaseModel

class ResumeText(BaseModel):
    text: str

@router.post("/extract-text")
async def extract_skills_from_text(
    data: ResumeText,
    job_role: str = "Software Developer",
    current_user=Depends(get_current_user)
):
    if not data.text or len(data.text) < 30:
        raise HTTPException(status_code=400, detail="Please provide more text.")

    resume_text = data.text[:3000]

    prompt = f"""
You are an expert technical recruiter reading a resume for a {job_role} position.

Resume text:
---
{resume_text}
---

Extract technical and professional skills. Rate each 0-10 based on evidence.
Extract 5-10 most relevant skills for {job_role}.

Return ONLY valid JSON, no markdown:
{{
  "extracted_skills": [
    {{"name": "<skill>", "level": <0-10>, "reason": "<one short sentence>"}}
  ],
  "summary": "<2 sentences about this candidate>"
}}
"""

    try:
        result = await ask_ai_json(prompt)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI extraction failed: {str(e)}")

    return {
        "extracted_skills": result.get("extracted_skills", []),
        "summary": result.get("summary", ""),
        "filename": "pasted-text"
    }
