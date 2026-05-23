from fastapi import APIRouter

router = APIRouter()

# These are just the job role cards shown on the homepage.
# Skills themselves are now analyzed by Gemini AI - not stored in a database.
JOB_ROLES = [
    {"id": 1,  "title": "Data Analyst",           "icon": "chart-bar",     "description": "Analyse data to help businesses make better decisions"},
    {"id": 2,  "title": "Frontend Developer",      "icon": "code",          "description": "Build beautiful websites and web applications"},
    {"id": 3,  "title": "Backend Developer",       "icon": "server",        "description": "Build APIs, databases and server-side logic"},
    {"id": 4,  "title": "Full Stack Developer",    "icon": "layers",        "description": "Work on both frontend and backend systems"},
    {"id": 5,  "title": "Machine Learning Engineer","icon": "cpu",           "description": "Build and deploy AI and ML models"},
    {"id": 6,  "title": "DevOps Engineer",         "icon": "settings",      "description": "Manage cloud infrastructure and deployment pipelines"},
    {"id": 7,  "title": "UI/UX Designer",          "icon": "palette",       "description": "Design user interfaces and experiences"},
    {"id": 8,  "title": "Cybersecurity Analyst",   "icon": "shield",        "description": "Protect systems and data from threats"},
    {"id": 9,  "title": "Cloud Architect",         "icon": "cloud",         "description": "Design and manage cloud infrastructure"},
    {"id": 10, "title": "Product Manager",         "icon": "briefcase",     "description": "Lead product strategy and development teams"},
    {"id": 11, "title": "Data Scientist",          "icon": "trending-up",   "description": "Extract insights from complex datasets using statistics and ML"},
    {"id": 12, "title": "Mobile Developer",        "icon": "smartphone",    "description": "Build iOS and Android mobile applications"},
]

@router.get("/roles")
async def get_roles():
    return JOB_ROLES

@router.get("/roles/{role_id}/skills")
async def get_role_skills(role_id: int):
    """
    Returns the key skills for a role so the analyzer page
    can show sliders to the user. Gemini will deeply analyze
    these when the user submits their ratings.
    """
    skills_map = {
        1:  ["SQL", "Python", "Excel", "Data Visualisation", "Statistics", "Power BI", "Communication"],
        2:  ["HTML & CSS", "JavaScript", "React", "Git", "Responsive Design", "TypeScript", "Performance Optimisation"],
        3:  ["Python", "REST APIs", "SQL", "Git", "Authentication", "Docker", "System Design"],
        4:  ["JavaScript", "React", "Node.js", "SQL", "Git", "Docker", "REST APIs"],
        5:  ["Python", "Machine Learning", "Deep Learning", "SQL", "Statistics", "MLOps", "Cloud Platforms"],
        6:  ["Linux", "Docker", "Kubernetes", "CI/CD", "Cloud (AWS/GCP/Azure)", "Scripting", "Monitoring"],
        7:  ["Figma", "User Research", "Wireframing", "Prototyping", "Design Systems", "Accessibility", "Communication"],
        8:  ["Networking", "Linux", "Security Frameworks", "Penetration Testing", "SIEM Tools", "Scripting", "Risk Assessment"],
        9:  ["AWS/GCP/Azure", "Networking", "Security", "Cost Optimisation", "Docker", "Terraform", "System Design"],
        10: ["Product Strategy", "Roadmapping", "User Research", "Data Analysis", "Communication", "Agile", "Stakeholder Management"],
        11: ["Python", "Statistics", "Machine Learning", "SQL", "Data Visualisation", "Storytelling", "Experimentation"],
        12: ["React Native / Flutter", "JavaScript or Dart", "REST APIs", "Git", "App Store Deployment", "UI Design", "Performance Optimisation"],
    }
    role = next((r for r in JOB_ROLES if r["id"] == role_id), None)
    if not role:
        return {"skills": []}
    return {
        "role": role["title"],
        "skills": skills_map.get(role_id, [])
    }
