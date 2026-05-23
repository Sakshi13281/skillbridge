from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import init_db
from routers import auth, skills, analysis, roadmap, dashboard, profile

app = FastAPI(title="SkillBridge API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup():
    await init_db()

app.include_router(auth.router,      prefix="/auth",      tags=["Auth"])
app.include_router(skills.router,    prefix="/skills",    tags=["Skills"])
app.include_router(analysis.router,  prefix="/analysis",  tags=["Analysis"])
app.include_router(roadmap.router,   prefix="/roadmap",   tags=["Roadmap"])
app.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])
app.include_router(profile.router,   prefix="/profile",   tags=["Profile"])

@app.get("/")
async def root():
    return {"message": "SkillBridge API is running"}
